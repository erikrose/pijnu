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
Generator

Parser generator.
~ Can generate a python parser module from text grammar.
~ Can return a parser object.
~ Can create a pattern from a format.
'''

### import/export
from pijnu.library.tools import fileText, writeFile
# pattern types for getPattern
from pijnu.library.pattern import *

# this is the standard meta parser --> makeParser
from pijnuParser import pijnuParser
# pattern objects to parse pattern format --> getPattern
from pijnuParser import pattern, patternDef

__all__ = ["getPattern","makeParser","fileText"]

### pattern generator
def getPattern(format):
    ''' pattern object as defined by format
        This is equivalent to hand-coding a pattern.
        ~ Allows using pijnu as a kind of regex lib.
        ~ Allows handy testing of specific pattern.
        ~ Note: is there an alternative to eval()?
        New: the pattern can be named! '''
    ''' example:
        digit = getPattern("[0..9]")            # anonymous
        digit = getPattern("digit : [0..9]")    # named
        '''
    ### parse source format
    format = format.strip()
    # case named
    try:
        format_ = "%s\n" % format
        patternNode = patternDef.parse(format_)
        (name,patternExpression) = patternNode.value.split("=",1)
        (name,patternExpression) = (name.rstrip(),patternExpression.lstrip())
    # case unnamed
    except PijnuError, e:
        try:
            patternNode = pattern.parse(format)
            patternExpression = patternNode.value
        # else error
        except PijnuError, e:
            message = "Invalid pattern format:\n   %s" %format
            raise PijnuError(message)

    ### yield & return pattern object
    print "... creating pattern from\n    %s" % format
    patternObject = eval(patternExpression)
    print "--> %s  %s" % (patternObject.__class__.__name__, patternObject)
    return patternObject

#
### parser generator
def makeParser(grammarText, feedback=False):
    ''' Write parser code file. '''
    ''' example:
        from pijnu import makeParser, fileText
        parser = makeParser(fileText("foo.pijnu")) '''
    ### parse & process grammar
    #   (using meta-parser 'pijnuParser')
    print "... parsing grammar ..."
    tree = pijnuParser.parse(grammarText)

    ### compose parser code:
    #   ~ copy of grammar original definition inside """..."""
    #   ~ "from pijnu.library import *"
    #   ~ parser object creation
    #   ~ grammar code itself
    #   ~ parser object specification
    print "... composing code ..."
    # major code sections
    grammarTitle = tree.title
    definition = tree.definition
    # parser object definition
    parserName = "%sParser" % grammarTitle
    topPatternName = tree.topPatternName
    filename = "%s.py" % parserName

    code = ('''%(definitionCopy)s
from pijnu.library import *


def make_parser(actions=None):
    """Return a parser.

    The parser's toolset functions are (optionally) augmented (or overridden)
    by a map of additional ones passed in.

    """
    if actions is None:
        actions = {}

    # Start off with the imported pijnu library functions:
    toolset = globals().copy()

    parser = Parser()
    state = parser.state

%(grammarCode)s

    symbols = locals().copy()
    symbols.update(actions)
    parser._recordPatterns(symbols)
    parser._setTopPattern("%(topPatternName)s")
    parser.grammarTitle = "%(grammarTitle)s"
    parser.filename = "%(filename)s"

    return parser\n''' %
    dict(definitionCopy='""" %s\n%s\n"""\n' % (grammarTitle, tree.definition),
         parserName=parserName,
         topPatternName=topPatternName,
         grammarTitle=grammarTitle,
         filename=filename,
         grammarCode='\n    '.join(tree.value.splitlines())))

    ### write parser module --possible feedback on stdout
    print "... writing file ...\n"
    writeFile(filename, code)
    if feedback:
        print fileText(filename)

    ### return parser object --if ever needed
    modulename = filename[:-3]
    module = __import__(modulename)
    return module.make_parser

#
#
#
####### test #####################################################
# Note: little code below is intended to quickly test a
#       failing pattern from a test grammar or meta-grammar.
#       Comment out when not needed anymore.
#~ from pijnuParser0 import patternLine, group
#~ source = "codeLine   : INDENT? CODECHAR+ EOL : join\n"
#~ patternLine.test(source)
#~ end()

#~ from additionParser import additionParser
#~ sources = "1+1 -1+1 12334+1 123+98765".split()
#~ additionParser.testSuiteDict(sources)
#~ end()

def genPattern():
    # TODO
    pass
def SebastienFunction():
    print ("=== sample: noTransform ===")
    # define
    SebastienFunctionGrammar = r"""
SebastienFunction
<toolset>
#   none
<definition>
#   simplified constants
SPACE       : ' '                                       : drop
SPACING     : SPACE+                                    : drop
LPAREN      : '('                                       : drop
RPAREN      : ')'                                       : drop
COMMA       : ','                                       : drop
DOC         : "\'\'\'"                                  : drop
FUNCSTART   : "@function"                               : drop
FUNCEND     : "@end"                                    : drop
COLON       : ':'                                       : drop
EOL         : '\n'                                      : drop
TAB         : '\t'
INDENT      : TAB / SPACE+                              : drop
DEDENT      : !INDENT
CODECHAR    : [\x20..\x7f  \t]
DOCCHAR     : [\x20..\x7f  \t\n]
IDENTIFIER  : [a..z  A..Z  _] [a..z  A..Z  0..9  _]*    : join
#   lower-level patterns
funcName    : SPACING IDENTIFIER SPACING?               : liftValue
argument    : IDENTIFIER
codeLine    : INDENT? CODECHAR+ EOL                     : join
#   func def
type        : COLON IDENTIFIER SPACING?                 : liftValue
typeDef     : type?                                     : keep
moreArg     : COMMA SPACE* argument                     : liftNode
argList     : LPAREN argument moreArg* RPAREN           : extract
arguments   : argList?                                  : keep
docBody     : INDENT* DOC (!DOC DOCCHAR)* DOC EOL?      : join
doc         : docBody?                                  : keep
codeBody    : INDENT codeLine+ DEDENT                   : liftValue
code        : codeBody?                                 : keep
funcDef     : FUNCSTART funcName typeDef arguments EOL doc code FUNCEND
"""
    makeParser(SebastienFunctionGrammar,"SebastienFunctionParser.py")
    # use
    from SebastienFunctionParser import SebastienFunctionParser
    source1 = """@function f1
@end"""
    SebastienFunctionParser.test(source1)
    source2 = """@function f2:typ (foo, bar, baz)
    ''' do it!
        and do it well!
        '''
    do this
    do that
@end"""
    SebastienFunctionParser.test(source2)
def klasses():
    print ("=== sample: klasses ===")
    klassesGrammar = r"""
klasses
<toolset>
def charFromEsc(node):
    node.value = node[0].value
def charFromDec(node):
    ord = int(node.value)
    node.value = chr(ord)
def charFromHex(node):
    ord = int(node.value, 16)
    node.value = chr(ord)
def charsetFromRanj(node):
    (n1,n2) = (ord(node[0].value),ord(node[1].value))
    chars = [chr(n) for n in range(n1, n2+1)]
    node.value = ''.join(chars)
def excludedCharset(node):
    (inCharset,exCharset) = (node[0].value,node[1].value)
    chars = [c for c in inCharset if c not in exCharset]
    node.value = ''.join(chars)
<definition>
# coding
    LBRACKET    : '['                                       : drop
    RBRACKET    : '\]'                                      : drop
    SEP         : "  "                                      : drop
    EXCLUSION   : "!!"                                      : drop
    RANGE       : ".."                                      : drop
    ESC         : "\\"                                      : drop
    DEC         : "\\"                                      : drop
    HEX         : "\\x"                                     : drop
    DECNUM      : [0..9]
    HEXNUM      : [0..9  a..eA..E]
# character expression
    safeChar    : !EXCLUSION [\x20..\x7e  !!\]]             : liftNode
    escChar     : ESC '\]'                                  : charFromEsc
    decChar     : DEC DECNUM{3}                             : join charFromDec
    hexChar     : HEX HEXNUM{2}                             : join charFromHex
    char        : hexChar / decChar / escChar / safeChar
# klass format
    ranj        : char RANGE char                           : charsetFromRanj
    klassItem   : SEP / ranj / char
    charset     : klassItem+                                : join
    exclCharset : charset EXCLUSION charset                 : excludedCharset
    klass       : LBRACKET (exclCharset / charset) RBRACKET : liftValue
"""
    makeParser(klassesGrammar)
    from klassesParser import klassesParser
    text = r"""[] [abc!'"\]] [a..e] [abcxyz  \097..\101] [\x61..\x65  1..9]"""
    print klassesParser.findAll(text)
    text = r"""[!!] [abc!!] [a!!b!!c] [abc!!b] [a..c  1..9  !'\]"  !!\'b  2..8]"""
    print klassesParser.findAll(text)
def numbers():
    print ("=== sample: numbers ===")
    numbersGrammar = """\
numbers
<toolset>
def toReal(node):
    node.value = float(node.value)
<definition>
SEP         : ' '
DOT         : '.'
digit       : [0..9]
integer     : digit+
real        : integer DOT integer?
number      : real / integer
numbers     : number (SEP number)*

"""
    makeParser(numbersGrammar)
    from numbersParser import numbersParser
    numbersParser.test("123 4. 5.67")
    print numbersParser.match("123 4. 5.67")
    numbersParser.integer.test("123 456 789", 'findAll')

def numbersTransform():
    print ("\n=== sample0: numbersTransform ===")
    numbersTransformGrammar = """\
numbersTransform
<toolset>
def toReal(node):
    node.value = float(node.value)
<definition>
SEP         : ' '                       : drop
DOT         : '.'
digit       : [0..9]
integer     : digit+                    : join
real        : integer DOT integer?      : join
number      : real / integer            : toReal
addedNum    : SEP number                : liftNode
numbers     : number (addedNum)*        : extract
"""
    makeParser(numbersTransformGrammar)
    from numbersTransformParser import numbersTransformParser
    numbersTransformParser.test("123 4. 5.67")

def formula():
    print ("=== sample1: formula ===")
    formulaGrammar = """\
formula
<toolset>
def doAdd(node):
    (n1,n2) = (node[0].value,node[1].value)
    node.value = n1 + n2
def doMult(node):
    (n1,n2) = (node[0].value,node[1].value)
    node.value = n1 * n2
<definition>
digit       : [0..9.]
number      : digit+                                        : join toReal
ADD         : '+'                                           : drop
MULT        : '*'                                           : drop
LPAREN      : '('                                           : drop
RPAREN      : ')'                                           : drop
mult        : (grup/number) MULT (grup/mult/number)         : @
add         : (grup/mult/number) ADD (grup/add/mult/number) : @
grup        : LPAREN (add / mult) RPAREN                    : @ liftNode
formula     : add / mult / digit
"""
    makeParser(formulaGrammar)
    # test
    from formulaParser import formulaParser
    formulaParser.test("9*8+01*2.3+45*67*(89+01.2)")
    print 9*8+01*2.3+45*67*(89+01.2)
    print formulaParser.match("9*8+01*2.3+45*67*(89+01.2)")
    Node.TREE_VIEW=True
    print formulaParser.match("9*8+01*2.3+45*67*(89+01.2)")

def wikInline():
    print ("=== sample: wikInline ===")
    wikInlineGrammar = """\
wikInline
<toolset>
def unescape(node):
    node.value = node[1].value
def styledSpan(node):
    klass = node.tag
    text = node.value
    node.value = '<span class="%s">%s</span>' %(klass,text)
<definition>
# codes
    ESCAPE          : '~'
    DISTINCT        : "//"                                  : drop
    IMPORTANT       : "!!"                                  : drop
    WARNING         : "**"                                  : drop
    styleCode       : (DISTINCT / IMPORTANT / WARNING)
# character expression
    escChar         : ESCAPE ('*' / '!' / '/' / ESCAPE)     : unescape
    validChar       : [\\x20..\\xff  !!/!*~]
    rawText         : (escChar / (!styleCode validChar))+   : join
# text kinds
    distinctText    : DISTINCT inlineText DISTINCT          : liftValue
    importantText   : IMPORTANT inlineText IMPORTANT        : liftValue
    warningText     : WARNING inlineText WARNING            : liftValue
    styledText      : distinctText / importantText / warningText    : styledSpan
    inlineText      : (styledText / rawText)+               : @ join
"""
    makeParser(wikInlineGrammar)
    from wikInlineParser import wikInlineParser
    # test
    text = "~~  ~*__~*~*__**~***__**~*~***__**X****X**"
    wikInlineParser.test(text)
    text = "aaa//bbb//!!ccc!!**ddd**//eee!!fff**ggg**hhh!!iii//jjj"
    wikInlineParser.test(text)
    text = "1//2!!3//!!4"
    wikInlineParser.test(text,"parseTest")

def wiki():
    print ("=== sample2: wiki ===")
    wikiGrammar = """\
wiki
<definition>
# codes
    DISTINCT        : "//"                              : drop
    IMPORTANT       : "!!"                              : drop
    WARNING         : "**"                              : drop
    ESCAPE          : '~'
# character expression
    escChar         : ESCAPE ('*' / '!' / '/')
    rawChar         : [\\x20..\\xff  !!/!*]
    lineChar        : [\\x20..\\xff]
    rawText         : rawChar+                          : join
# text
    distinctText    : DISTINCT inline DISTINCT          : liftValue
    importantText   : IMPORTANT inline IMPORTANT        : liftValue
    warningText : WARNING inline WARNING        : liftValue
    styledText      : distinctText / importantText / warningText
    text            : styledText / rawText
    inline          : text+                             : @
# line types
    LF              : '\n'
    CR              : '\r'
    EOL             : (LF/CR)+                              : drop
    BULLETLIST      : "*"                                   : drop
    NUMBERLIST      : "#"                                   : drop
    TITLE           : "="                                   : drop
    paragraf        : !(BULLETLIST/NUMBERLIST) inline EOL   : liftValue
    paragrafs       : paragraf+
    bulletListItem  : BULLETLIST inline EOL                 : liftValue
    bulletList      : bulletListItem+
    numberListItem  : NUMBERLIST inline EOL                 : liftValue
    numberList      : numberListItem+
    blankLine       : EOL
    body            : (bulletList / numberList / paragrafs / blankLine)+
    #body           : (bulletListItem / numberListItem / paragraf / blankLine)+
    title           : TITLE inline EOL                  : liftValue
    text            : blankLine* title? body
"""
    makeParser(wikiGrammar)
    from wikiParser import wikiParser
    # test inline
    inline = "a //bb// !!cc!! d //ee !!fff __ggggg__ hhh!! ii// j"
    wikiParser.inline.test(inline)
    # test wikitext
    wikiText = """

=F1 - !!GP de Malaisie!! -- //Du malaise dans l'air//
Moins d'une semaine après l'ouverture des festivités (hostilités ?) à Melbourne,
le //Formula One Circus// installe son barnum en Malaisie,
sur le circuit de Sepang.
Un tracé que les ingénieurs et les pilotes connaissent dans ses moindres recoins.
Situé au beau milieu de la jungle,
Sepang est un peu le //jardin// de !!Ferrari!! qui y totalise cinq succès en dix courses.
Mais en ce début de saison,
la //nouvelle !!réglementation!! technique// a eu pour effet de chambouler la hiérarchie.

Et si Brawn GP devrait rester aux avant postes, les gros bras
* Ferrari
* McLaren
* !!Renault!! devraient sensiblement réduire l'écart.

Suffisamment pour vaincre ? Pas si sûr, car
# BMW et Kubica ont été rapides à //Melbourne//,
# Williams
# Toyota
# Red Bull
ont également prouvé un haut niveau de performances.
"""
    wikiParser.test(wikiText)

def meta():
    # pijnu self meta parsing (!)
    print ("=== sample3: metaMeta ===")
    pijnuGrammar = open("pijnu.test",'r').read()
    makeParser(pijnuGrammar,"pijnuParser1.py")
    end()   ################################################################
    ### test produced meta parser
    from pijnuParser1 import pijnuParser
    print ("\n=== meta meta test ===")
    # test with debug grammar
    debugGrammar = """\
# with recursive patterns
debug
<toolset>
def toReal(node):
    node.value = float(node.value)
<definition>
SEP         : ' '                       : drop
DOT         : '.'
digit       : [0..9]
integer     : digit+                    : join
real        : integer DOT integer?      : debug join
number      : real / integer            : toReal
# top pattern
moreNum     : SEP number                : liftNode
numbers     : number (moreNum)*         : extract
"""
    print ("\n=== writing debug parser")
    makeParser(debugGrammar, "debug.py", pijnuParser)
    print ("\n=== testing debug parser")
    from debug import debugParser
    debugParser.digit.test("9 8 . 7", "findAll")
    debugParser.test("9 9.9 999.99 0.")
    # test with formula grammar
    formulaGrammar = """\
formula
<definition>
{
digit       : [0..9.]
number      : digit+                                        : join real
ADD         : '+'                                           : drop
MULT        : '*'                                           : drop
LPAREN      : '('                                           : drop
RPAREN      : ')'                                           : drop
multTerm    : grup / number
moreMult    : MULT multTerm                                 : liftNode
mult        : (grup/number) MULT (grup/mult/number)         : @
addTerm     : grup / mult / number
moreAdd     : ADD multTerm                                  : liftNode
add         : (grup/mult/number) ADD (grup/add/mult/number) : @
grup        : LPAREN (add / mult) RPAREN                    : @ liftNode
formula     : add / mult / digit
}
"""
    print ("\n=== writing formula parser")
    makeParser(formulaGrammar, "formula.py", pijnuParser)
    print ("\n=== testing formula parser")
    from formula import formulaParser
    formulaParser.test("9*8+01*2.3+45*67*(89+01.2)")
    # test with wiki grammar
    wikiGrammar = """\
wiki
<definition>
{
# inline text
    lineChar        : [\\x20..\\xff]
    rawChar         : [\\x20..\\xff  !!/!_]
    DISTINCT        : "//"                              : drop
    IMPORTANT       : "!!"                              : drop
    MONOSPACE       : "__"                              : drop
    rawText         : rawChar+                          : join
    distinctText    : DISTINCT inline DISTINCT          : liftValue
    importantText   : IMPORTANT inline IMPORTANT        : liftValue
    warningText : MONOSPACE inline MONOSPACE        : liftValue
    styledText      : distinctText / importantText / warningText
    text            : styledText / rawText
    inline          : text+                             : @
# line types
    LF              : '\n'
    CR              : '\r'
    EOL             : (LF/CR)+                              : drop
    BULLETLIST      : "*"                                   : drop
    NUMBERLIST      : "#"                                   : drop
    TITLE           : "="                                   : drop
    paragraf        : !(BULLETLIST/NUMBERLIST) inline EOL   : liftValue
    paragrafs       : paragraf+
    bulletListItem  : BULLETLIST inline EOL                 : liftValue
    bulletList      : bulletListItem+
    numberListItem  : NUMBERLIST inline EOL                 : liftValue
    numberList      : numberListItem+
    blankLine       : EOL
    body            : (bulletList / numberList / paragrafs / blankLine)+
    #body           : (bulletListItem / numberListItem / paragraf / blankLine)+
    title           : TITLE inline EOL                  : liftValue
    text            : blankLine* title? body
}
"""
    print ("\n=== writing wiki parser")
    makeParser(wikiGrammar, "wiki.py", pijnuParser)
    from wiki import wikiParser
    inline = "a //bb// !!cc!! d //ee !!fff __ggggg__ hhh!! ii// j"
    wikiParser.inline.test(inline)
    wikiText = """

=F1 - !!GP de Malaisie!! -- //Du malaise dans l'air//
Moins d'une semaine après l'ouverture des festivités (hostilités ?) à Melbourne,
le //Formula One Circus// installe son barnum en Malaisie,
sur le circuit de Sepang.
Un tracé que les ingénieurs et les pilotes connaissent dans ses moindres recoins.
Situé au beau milieu de la jungle,
Sepang est un peu le //jardin// de !!Ferrari!! qui y totalise cinq succès en dix courses.
Mais en ce début de saison,
la //nouvelle !!réglementation!! technique// a eu pour effet de chambouler la hiérarchie.

Et si Brawn GP devrait rester aux avant postes, les gros bras
* Ferrari
* McLaren
* !!Renault!! devraient sensiblement réduire l'écart.

Suffisamment pour vaincre ? Pas si sûr, car
# BMW et Kubica ont été rapides à //Melbourne//,
# Williams
# Toyota
# Red Bull
ont également prouvé un haut niveau de performances.
"""
    wikiParser.test(wikiText)

def test():
#~  genPattern()
#~  print RULER
#~  klasses()
#~  print RULER
#~  SebastienFunction()
#~  print RULER
#~  numbers()
#~  print RULER
#~  numbersTransform()
#~  print RULER
#~  formula()
#~  print RULER
#~  wikInline()
#~  print RULER
#~  wiki()
#~  print RULER
#~  meta()
    pass
if __name__ == "__main__":
#~  test()
    pass

