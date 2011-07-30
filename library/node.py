# -*- coding: utf8 -*-

'''
© 2009 Denis Derman (former developer) <denis.spir@gmail.com>
© 2011 Peter Potrowl (current developer) <peter017@gmail.com>

This file is part of PIJNU.

PIJNU is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PIJNU is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PIJNU: see the file called 'GPL'.
If not, see <http://www.gnu.org/licenses/>.
'''


'''     N o d e   t y p e

    A node basically holds one or more match results.
    A node is yielded by a successful match check.
    It is an element of parse tree.
    Structurally speaking, it is a kind of tree/node
        ~ which 'tag' attribute is given by the pattern's name,
        ~ that can be either a leaf or branch node,
        ~ that can be 'nil', a special case of leaf node.

    The 'value' attribute
        ~ originally holds the snippet of source matched in case of a leaf,
        ~ originally holds a sequence of child nodes in case of a branch,
        ~ can be modified by match actions assigned to the pattern.

    Try & use the treeView output format!

    Notes:
        ~ Holds all useful information, including type & interval in source.
        ~ Node is a recursive type, i.e. image of a parse tree:
        ~ You can use standard or custom action methods to modify a node.
        ~ Several output formats.
'''

'''     m a t c h   a c t i o n s

    This is a set of standard match actions
    used to modify a node's structure or value.
    Action methods defined for a pattern are automatically launched
    after each successful match, on the generated node.
    This is a very simple and powerful tool.
    You can write custom match actions for your language
    and put them in the 'toolset' section of the grammar.

    Each action accepts a single parameter: the node.
    Node's interesting attributes:
        * ... whatever you set on it!
        * type      : the pattern's name
        * value     : ...
        * text      : the matched snippet in source text
        * start,stop: the interval in source text
        * kind      : either Node.BRANCH or Node.LEAF
        * Node.NIL  : special value for successful but empty match

    There are several kinds of standard match actions:
    (branch: node which value is a sequence of child nodes)
    (singleton: branch node with a single child node)

    = debug =
    ~ debugOutput:  a function intended to write full information
                    (with TREE_VIEW & WHOLE_INFO)
                    about nodes yielded by a pattern
                    which result is not what one expects.
    Use it!

    = structure =
    ~ liftValue:    (singleton) lift child value (type is kept)
    ~ liftNode:     (singleton) lift child node (type too)
    ~ extract:      (branch) extract nested branches' node (flatten 1 level)
    ~ toLeaves:     (branch) collect all leaf nodes only (flatten leaves)

    = list handling
    ~ intoList:     actions a messy result of a pattern
                    expressing a separated list of items
                    into a simple list of items nodes
    Super handy!

    = value =
    Value change is necessarily ad hoc, expect for:
    ~ drop:     set value to nil -- will be cancelled at higher level
    ~ join:     (uses leaves) glue leaf values into single a string
    ~ integer:  convert value to int
    ~ real:     convert value to float
'''


### import/export
from tools import *
__transforms__ = [
        "debugOutput",
        "liftValue", "liftNode", "extract", "toLeaves", "intoList",
        "drop", "keep", "join", "restore",
        "toInt", "toFloat", "collectValues",
        ]
__all__ = ["Node", "Nodes"] + __transforms__


################## node object ####################
# sequence of child nodes for a branch node
class Nodes(Seq):
    ''' node sequence
        ~ subtype of 'Seq', a custom version of list
        ~ used to distinguish a sequence of real child nodes
          from a node value that just happens to be sequential
          (possibly resulting of user defined action)
        '''
    pass


# nil node value type
class Nil(object):
    def __repr__(self):
        return "Ø"

    def __unicode__(self):
        return u"Ø"


### Node
class Node(object):
    ''' parse tree node
        -- can represent a whole parse tree

        Aspects worth a look:
            ~ type: <-- pattern name as minimal semantic info
            ~ nil value for empty results to be erased
            ~ kind: branch or leaf
            ~ possible children are held inside value of type Nodes
            ~ standard match actions available
            ~ interval in source text: start_pos, end_pos
            ~ __repr__: type:value format or full output
            ~ treeView: excellent for design/setup/debug
    '''

    ### output config
    TREE_VIEW = False
    WHOLE_INFO = False

    ### constants -- defined in module doActions
    # 'NIL' node value ~ successful but empty match result to be erased
    NIL = Nil()
    # enumeration for node 'kind' attribute
    (LEAF, BRANCH) = (1, 2)

    ### creation, value, action
    def __init__(self, pattern, value, start, end, source):
        ''' Define pattern, tag, value, kind, range.
        '''
        # base info
        self.tag = pattern.name         # the most important information?
        self.value = value              # node value -- can be transformed

        # additional info
        self.pattern = pattern          # this node's generator
        self.form = value               # initial value form -- case doActions
        self.defineKind()               # LEAF / BRANCH

        # source
        self.source = source               # whole source text
        self.start, self.end = start, end  # interval in source -- end excluded
        self.snippet = source[start:end]   # matched source text snippet

        # clean up branch node's sequential value
        if self.kind is Node.BRANCH:
            self.cleanBranch()

        # apply match actions to transform node's value
        if pattern.actions is not None:
            self.doActions(pattern.actions)

    def defineKind(self):
        ''' Define node's kind, meaning whether it is
            leaf (single) or branch (sequential).
        '''
        if isinstance(self.value, Nodes):
            self.kind = Node.BRANCH
        # else should be leaf node
        # -- basically a string
        else:
            self.kind = Node.LEAF

    def cleanBranch(self):
        ''' Clean up branch node's sequential value.
        '''
        # Drop nil values.
        childNodes = Nodes()
        for childNode in self.value:
            if childNode.value != Node.NIL:
                childNodes.append(childNode)
        self.value = childNodes
        # If then empty, change kind to LEAF & value to nil.
        if len(self.value) == 0:
            self.value = Node.NIL
            self.kind = Node.LEAF

    def doActions(self, actions):
        ''' Apply match actions to node / value.
        '''
        for action in actions:
            action(self)
        # redefine node kind if ever (often reduced to single LEAF)
        self.defineKind()

    ### iteration on child nodes, or value items
    def __getitem__(self, index):
        ''' Get a child node, or a value item.
            Just a trick to avoid:
            ~ "node.value[index]"       -- write "node[index]"
            ~ "for child in node.value" -- write "for child in node"
        '''
        try:
            return self.value[index]
        except TypeError:
            message = "Node %s\nis a leaf node without child nodes." % self
            raise TypeError(message)

    def __delitem__(self, index):
        ''' Delete a child node, or a value item.
        '''
        try:
            del self.value[index]
        except TypeError:
            message = "Node %s\nis a leaf node without child nodes." % self
            raise TypeError(message)

    def __len__(self):
        ''' number child nodes
        '''
        try:
            return len(self.value)
        except TypeError:
            message = "Node %s\nis a leaf node without child nodes." % self
            raise TypeError(message)

    def __unicode__(self):
        if isinstance(self.value, Nodes):
            return "%s:%s" % (self.tag, unicode(self.value))
        return "%s:'%s'" % (self.tag, unicode(self.value))

    ### output
    def leaf(self):
        if isinstance(self.value, Nodes):
            value = ''.join(item.leaf() for item in self.value)
            return value
        return self.value

    def __repr__(self):
        ''' output format "type:value"
        '''
        return "%s:%s" % (self.tag, repr(self.value))

    def __str__(self):
        ''' output format "type:value", or whole information, or treeView(),
            according to WHOLE_INFO & TREE_VIEW config
        '''
        if Node.TREE_VIEW:
            return self.treeView()
        if Node.WHOLE_INFO:
            return "%s <= %s <= %s <%s..%s>" % (repr(self),
                    repr(self.form), repr(self.snippet), self.start, self.end)
        return repr(self)

    def treeView(self, level=0):
        ''' recursive tree view
        '''
        TAB = "   "
        indent = level * TAB
        # format according to WHOLE_INFO
        if Node.WHOLE_INFO:
            format = "%s%s:" \
                     "\n%s%srange: <%s..%s>" \
                     "\n%s%stext : %s" \
                     "\n%s%sform : %s" \
                     "\n%s%svalue: " \
                    % (indent, self.tag,
                       indent, TAB, self.start, self.end,
                       indent, TAB, repr(self.snippet),
                       indent, TAB, repr(self.form),
                       indent, TAB)
            level += 1
        else:
            format = "%s%s:" % (indent, self.tag)
        # value according to LEAF / BRANCH kind
        if self.kind is Node.LEAF:
            value = self.value
        else:
            value = ""
            for child in self.value:
                value += "\n%s" % (child.treeView(level + 1))
        # whole tree
        return "%s%s" % (format, value)

    def leaves(self):
        '''Recursively returns the leaves of the node tree'''
        if self.kind is Node.LEAF:
            value = self.value
        else:
            value = ""
            for child in self.value:
                if isinstance(child, Node):
                    value += "%s" % (child.leaves())
                else:
                    value += "%s" % child
        return "%s" % (value)

################## match actions ####################
### debug
def debugOutput(node):
    ''' Output full info about a node.
        ~ Intended to debug a pattern that does not work properly.
    '''
    ROW = 33 * '?'
    saveConfig = (Node.TREE_VIEW, Node.WHOLE_INFO)
    (Node.TREE_VIEW, Node.WHOLE_INFO) = (True, True)
    print "%s\n%s\n%s" % (ROW, node, ROW)
    (Node.TREE_VIEW, Node.WHOLE_INFO) = saveConfig


### node structure handling
def liftValue(node):
    ''' Set a singleton node's value to its nested node value.
        ~ Id est lift up nested value.
        ~ Applies only on singleton nodes.
        * Contrast with liftNode.
    '''
    ''' example
        hex     : ...
        dec     : ...
        HEXKOD  : '\\x'                         : drop
        DECKOD  : '\\'                          : drop
        num     : ((HEXKOD hex) / (DECKOD dec)) : extract
        nums    : num+
        The pattern num will produce singleton node holding either hex or dec.
        Without extract, the result tree looks like:
        nums
            num:
                hex:value
            num:
                dec:value
        With extract, the result tree looks like:
        nums
            num:value
            num:value
    '''
    if node.kind is Node.LEAF:
        return
    if len(node) != 1:
        return
    if isinstance(node[0], unicode) or isinstance(node[0], str):
        node = node[0]
        return
    node.value = node[0].value


def liftNode(node):
    ''' Set a singleton node's data to its nested node data.
        ~ Id est lift up nested node.
        ~ Applies only on singleton nodes..
        * Contrast with liftValue.
    '''
    ''' example
        LPAREN  : '('                       : drop
        RPAREN  : ')'                       : drop
        pat1    : LPAREN (x / y / z) RPAREN : lift
        pat2    : u / v / w
        pat     : pat1 pat2
        The pattern pat1 will yield singleton branch nodes,
        holding only an x/y/z child -- for parens are dropped.
        Without lift, the result tree looks like:
        pat:
            pat1:
                y:value
            v:value
        With lift, the result tree looks like:
        pat:
            y:value
            v:value
    '''
    # exclude leaf & singleton nodes
    if node.kind is Node.LEAF:
        return
    if len(node) != 1:
        return
    # lift child node
    # Cannot simply copy or replace node, for node id must remain.
    child = node[0]
    (node.tag, node.value) = (child.tag, child.value)


def extract(node):
    ''' Extract a branch node's directly nested branches' child nodes.
        ~ Id est flatten one nesting level.
        ~ Applies only on branch nodes.
        * Contrast with leaves.
    '''
    ''' action:
        [1 [21 22] [31 32]]                 ==> [1 21 22 31 32]
        [1 [21 22] [31 [321 322] [[33]]]]   ==> [1 21 22 31 [321 322] [[33]]]
    '''
    ''' example:
        LPAREN      : '('                   : drop
        RPAREN      : ')'                   : drop
        SEP         : ", " / ","            : drop
        item        : ...
        moreItems   : (SEP item)*
        sequence    : item moreItems        : leaves
        The pattern seq will yield a sequential node
        holding a leaf and a nested branch.
        Without leaves, the result tree looks like:
        sequence:
            item:value
            moreItems:
                <?>:
                    item:value
                <?>:
                    item:value
        (where <?> is the anonymous "SEP item" pattern)
        With leaves, the result tree looks like:
        sequence:
            item:value
            item:value
            item:value
    '''
    if node.kind is Node.LEAF:
        return
    childNodes = Nodes()
    for childNode in node.value:
        if childNode.kind is Node.BRANCH:
            childNodes.extend(childNode.value)
        else:
            childNodes.append(childNode)
    node.value = childNodes


def toLeaves(node):
    ''' Set a branch node's value to a sequence of its terminal leaf nodes.
        ~ Id est flatten the nested node tree, but keeping leaves only.
        ~ Applies only on branch nodes.
        * Contrast with leaves.
    '''
    ''' action:
        [1 [21 22] [31 [321 322] [[33]]]]    ==> [1 21 22 31 321 322 33]
    '''
    if node.kind is Node.LEAF:
        return
    childNodes = Nodes()
    for childNode in node.value:
        # recursion: first doActions branch child to leaves itself
        if childNode.kind == Node.LEAF:
            childNodes.append(childNode)
        # recursion: first doActions branch child to leaves itself
        else:
            toLeaves(childNode)
            childNodes.extend(childNode.value)
    node.value = childNodes


def intoList(node):
    ''' Form a simple list from the value of a node
        generated by a pattern for a list of items.

        The issue is that the parse tree is messy:
            itemList    : item (SEP item)*
            ==>
            itemList:[item  [[SEP  item]  [SEP  item]...]]
        What we want is:
            itemList:[item  item  item...]

        'intoList' will also deal with patterns for
        operations that allow more than 2 operands:
            operation   : oper OP oper (OP oper)*
            ==>
            operation:[oper  OP  oper  [[SEP  oper]  [SEP  oper]...]]
        Using intoList we get:
            operation:[oper  oper  oper  oper...]
    '''
    ''' If Separators are dropped, use extract twice instead:
            itemList:[item  [[item]  [item]...]]
            itemList:[item  [item]  [item]...]
            itemList:[item  item  item...]
    '''
    # case leaf or empty result
    if node.kind is Node.LEAF or len(node) == 0:
        return
    # flatten node list using extract twice
    extract(node)
    extract(node)
    # collect every child nodes, skipping seps
    items = Nodes()
    for i in range(0, len(node), 2):
        items.append(node[i])
    # new node value
    node.value = items
    print "intoList:", node


### value
def drop(node):
    ''' Set node value to nil (Node.NIL):
        ~ This will cause the node to be erased
          from higher-level branch node.
        * This is the opposite of keep.
    '''
    node.value = Node.NIL


def keep(node):
    ''' Set node value to '':
        ~ This will prevent nil node to be erased
          from higher-level branch node.
        ~ Applies only on nil nodes.
        * This is the opposite of drop.
    '''
    ''' usage:
        This is a handy func to set on optional parts of a sequence:
        then, the higher-level result always has the same structure
        and is consequently much easier to process.
        X   : 'x'
        Y   : 'y'?      : keep
        Z   : 'z'
        P   : X Y Z
        source = "xz" -->
        P:[X:'x'  Y:''  Z:'z']
    '''
    if node.value is Node.NIL:
        node.value = ''
        # case Option pattern:
        # use wrapped pattern's name as node type
        # so that the node always has the same name
        try:
            assert node.pattern.isOption == True
            node.tag = node.pattern.pattern.name
        except (AssertionError, AttributeError):
            pass


def restore(node):
    ''' Restore node value to original source text snippet.
        ~ Seems, stupid ;-), but in the meantime
          pattern has been matched: format is OK.
    '''
    node.value = node.snippet


def join(node):
    ''' Join branch node's leaves into single string.
        ~ Applies only on branch nodes.
        ~ Note: node becomes a leaf!
        ~ join() uses toLeaves()
    '''
    ''' usage:
        op          : '+' / '-' / '*' / '/'
        hexNum      : [0..9  a..eA..E]+     : hexToDec
        operation   : hexNum op hexNum      : join
        (hexToDec tranformation converts)
        source          "c-9 a0*ff 33/a"
        method          scan
        result          ['12-9'  '160*255'  '51/10']
    '''
    if node.kind is Node.LEAF:
        return
    toLeaves(node)
    childTexts = []
    for child in node.value:
        if isinstance(child.value, unicode):
            childTexts.append(unicode(child.value))
        else:
            childTexts.append(str(child.value))
    node.value = ''.join(childTexts)


def toInt(node):
    ''' Convert node value to python int.
    '''
    node.value = int(node.value)


def toFloat(node):
    ''' Convert node value to python float.
    '''
    node.value = float(node.value)


def collectValues(node):
    ''' Convert node value to tuple of child values.
        ~ Note: node becomes a leaf!
        ~ Applies only on branch nodes.
    '''
    ''' usage:
        add:[int:123 real:9.87]
        -->
        add:(123, 9.87)

        Then, in match actions, one can directly access
        data that were previously child values (*):
        def doAdd(node):
            (op1,op2) = node
            return op1 + op2
        ... instead of ...
        def doAdd(node):
            (op1,op2) = (node[1].value,node[2].value)
            return op1 + op2

        (*) Note that item access in node is magically directed to its value
        through overloading of __getitem___ (and __delitem__ and __len__).
    '''
    print "* collectValues:", node,
    node.value = tuple(child.value for child in node)
    print "-->", node


################## test ####################
# Pattern simulation
class Pat(object):
    def __init__(self, name, actions=None):
        self.name = name
        self.memo = dict()
        self.actions = actions

    def node(self, value, start, stop, source):
        return Node(self, value, start, stop, source)


def testLeaf():
    print ("=== simple leaf node ===")
    text = "val a b c"
    pat = Pat("pat")
    for v in (Node.NIL,
              'val ',
              'a b c'):
        n = pat.node(v, 0, 0, text)
        print ("%s:   -->   %s" % (v, n))


def testBranch():
    print ("=== sequential branch node ===")
    text = "0a+0b*0c"
    # patterns
    op = Pat("op")
    num = Pat("num")
    comp = Pat("comp")
    # nodes
    plus = op.node('+', 2, 3, text)
    star = op.node('*', 5, 6, text)
    un = num.node('0a', 0, 2, text)
    du = num.node('0b', 3, 5, text)
    tri = num.node('0c', 6, 8, text)
    un.value, du.value, tri.value = 10, 11, 12
    mult = comp.node(Nodes(du, star, tri), 3, 8, text)
    add = comp.node(Nodes(un, plus, mult), 0, 8, text)
    # output
    print """'mult' is parse result from "0b*0c" (hex)"""
    print """'add'  is parse result from "0a+0b*0c" """
    print "=== base output:"
    print "-mult-\n", mult
    print "-add-\n", add
    print "=== tree view:"
    Node.TREE_VIEW = True
    print "-mult-\n", mult
    print "-add-\n", add
    print "=== whole info:"
    Node.WHOLE_INFO = True
    Node.TREE_VIEW = False
    print "-mult-\n", mult
    print "-add-\n", add
    print "=== whole tree view:"
    Node.TREE_VIEW = True
    print "-mult-\n", mult
    print "-add-\n", add
    # after value computation
    print "\n*** (value computed) ***"
    mult.value, add.value = 131, 141
    mult.kind, add.kind = Node.LEAF, Node.LEAF
    print "=== whole info:"
    Node.WHOLE_INFO = True
    Node.TREE_VIEW = False
    print "-mult-\n", mult
    print "-add-\n", add
    print "=== whole tree view:"
    Node.TREE_VIEW = True
    print "-mult-\n", mult
    print "-add-\n", add


def testAction():
    print ("=== action ===")
    print "      (join only)"
    text = "0a+0b*0c"
    # patterns
    op = Pat("op")
    num = Pat("num")
    comp = Pat("comp", (join, ))
    # nodes
    plus = op.node('+', 2, 3, text)
    star = op.node('*', 5, 6, text)
    un = num.node('0a', 0, 2, text)
    du = num.node('0b', 3, 5, text)
    tri = num.node('0c', 6, 8, text)
    un.value, du.value, tri.value = 10, 11, 12
    mult = comp.node(Nodes(du, star, tri), 3, 8, text)
    add = comp.node(Nodes(un, plus, mult), 0, 8, text)
    # output
    Node.WHOLE_INFO = True
    Node.TREE_VIEW = False
    print "-mult-\n", mult
    print "-add-\n", add


def test():
    testLeaf()
    print RULER
    testBranch()
    print RULER
    testAction()


if __name__ == "__main__":
    test()
