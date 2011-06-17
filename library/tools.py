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

'''
Overall python toolset
'''

### import export
import sys
from sys import exit as end
from copy import copy, deepcopy as clone
from sets import Set

# end
end = sys.exit

__all__ = [
          "end", "output", "write",
          "Set", "Seq", "OrDict", "copy", "clone",
          "NL", "SPC", "TAB", "SPC3", "RULER",
          "fileText", "writeFile",
          ]

# ===   b a s i c   o u t p u t   t o o l s e t   ===============
# output target
output = sys.stdout
write = output.write
# constants
(SPC, TAB, NL, SPC3, RULER) = (' ', '\t', '\n', "   ", 33 * '=')


# typing
def typ(object):
    try:
        return object.__class__
    except AttributeError:
        return type(obj)


def typName(object):
    try:
        return object.__class__.__name__
    except AttributeError:
        return str(type(obj))


# textual output
def view(*objects):
    ''' return typed view of object(s) '''
    texts = list()
    for obj in objects:
        obj_view = "%s:%s" % (typName(obj), obj)
        texts.append(obj_view)
    return join(texts, "\n")


def show(*objects):
    print (view(*objects))


def viewSeq(seq):
    ''' return typed view of sequence with indented view of items '''
    text = view(seq)
    for item in seq:
        text += "\n\t%s" % view(item)
    return text


def showSeq(seq):
    print (viewSeq(seq))


def treeView(obj, level=0, show_groups=False):
    ''' return full indented treeView view of nested objuence '''
    indent = level * '\t'
    # case string ot not iterable: end recursion
    if (isinstance(obj, basestring) or not hasattr(obj, "__getitem__")):
        text = "%s%s\n" % (indent, view(obj))
        return text
    # case iterable: recursion
    obj_view = view(obj) if show_groups else typName(obj)
    text = "%s%s\n" % (indent, obj_view)
    for item in obj:
        text += treeView(item, level + 1)
    return text


# === custom sequence type ======================================
class Seq(list):
    ''' custom sequence
        ~ str() shows nested items' str()
        ~ able to show as treeView for clear output
        ~ implements leaves to flatten nested seqs
        '''

    def __init__(self, *seq):
        ''' create seq as a specialized list
            ~ arg can be either a single sequential object
              (possibly nesting other sequences)
              or a *tuple of items
              (each possibly a sequence)
             ~ nested sequences will recursively be converted to Seq '''
        # case seq is/holds a sequence
        # (conversion of a sequence into Seq object)
        if (len(seq) == 1 and isinstance(seq[0], (list, tuple, Seq, Set))):
            seq = seq[0]
        # then convert nested sequences
        items = []
        for item in seq:
            if isinstance(item, (list, tuple, Seq, Set)):
                items.append(Seq(item))
            else:
                items.append(item)
        # finally pass result as list init arg
        list.__init__(self, items)

    def __getitem__(self, index):
        return list.__getitem__(self, index)

    def __add__(self, other):
        return Seq(list.__add__(self, other))

    def __repr__(self):
        itemText = "  ".join(repr(item) for item in self)
        return "[%s]" % itemText
    
    def __unicode__(self):
        itemText = u"  ".join(unicode(item) for item in self)
        return "[%s]" % itemText

    def __str__(self):
        itemText = "  ".join(str(item) for item in self)
        return "[%s]" % itemText

    def treeView(self, level=0, show_groups=False):
        TAB = '   '
        indent = TAB * level
        if show_groups:
            text = "%s%s" % (indent, self)
        else:
            text = "%s<seq>" % indent
        level += 1
        indent += TAB
        for item in self:
            if isinstance(item, Seq):
                text += NL + item.treeView(level, show_groups)
            else:
                text += "%s%s%s" % (NL, indent, item)
        return text

    def leaves(self):
        leaves = Seq()
        for item in self:
            if isinstance(item, Seq):
                leaves += item.leaves()
            else:
                leaves.append(item)
        return leaves

    def flat(self):
        items = Seq()
        for item in self:
            items.append(item)
            if isinstance(item, Seq):
                items += item.flat()
        return items


# === custom ordered dict: OrDict ===============================
class OrDict(dict):
    ''' custom ordered dict
        ~ keeps order of keys as registered
        ~ beware of init (cannot pass dict)
        '''

    def __init__(self, *kvs):
        # kvs is a sequence of (k,v) pairs -- use:
        # r = Reg(('a',1), ('b',2), ('c',3))
        # or l = [('a',1), ('b',2), ('c',3)] ; r = Reg(*l)
        # Note: it's the only way to keep order (**kwargs is unordered)
        self.keyList = list()
        if kvs:
            for (k, v) in kvs:
                self.keyList.append(k)
                self[k] = v
    ### item access

    def __getitem__(self, k):
        return self.__dict__[k]

    def __setitem__(self, k, v):
        self.__dict__[k] = v
        if k not in self.keyList:
            self.keyList.append(k)

    def __delitem__(self, k):
        del self.__dict__[k]
        self.keyList.remove(k)

    def pop(self, k):
        v = self[k]
        self.__delitem__(k)
        return v

    ### ordered iteration
    def __iter__(self):
        ''' ordered iterator '''
        return iter(self.keyList)

    def keys(self):
        ''' dict keys '''
        return self.keyList

    def values(self):
        ''' dict values '''
        return [self[k] for k in self.keyList]

    def items(self):
        ''' dict items = (key:value) pairs '''
        return [(k, self[k]) for k in self.keyList]

    def sort(self):
        ''' Sort dict (keys). '''
        self.keyList.sort()

    ### dict combination
    def update(self, r):
        ''' Update from other dict. '''
        for k, v in r.items():
            self.__setitem__(k, v)

    def __add__(self, r):
        ''' new sum dict '''
        sum = clone(self)
        sum.update(r)
        return sum

    def copy(self):
        ''' dict deep copy '''
        return clone(self)

    ### output
    def __str__(self):
        ''' standard output '''
        pairs = ["%s:%s" % (k, v) for (k, v) in self.items()]
        return "{%s}" % "  ".join(pairs)

    def treeItems(self, level=1, TAB="   "):
        ''' view as item tree '''
        indent, LF = TAB * level, '\n'
        pairs = ["%s%s:%s" % (indent, k, v) for (k, v) in self.items()]
        return LF.join(pairs)


# === file tools ===============================
# === file & dir tools ===========================================
def fileText(filename):
    ''' file text
        -- with file object safely closed & filesystem file unlocked '''
    f = file(filename)
    text = f.read()
    f.close()
    return text


def writeFile(filename, text):
    ''' Write -- or overwrite -- text into file.
        --  No error if file exists '''
    f = file(filename, 'w')
    f.write(text)
    f.close()
