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

"""
<definition>
#	simplified constants
SPACE		: ' '										: drop
SPACING		: SPACE+									: drop
LPAREN		: '('										: drop
RPAREN		: ')'										: drop
COMMA		: ','										: drop
DOC			: "\'\'\'"									: drop
FUNCSTART	: "@function"								: drop
FUNCEND		: "@end"									: drop
COLON		: ':'										: drop
EOL			: '\n'										: drop
TAB			: '\t'
INDENT		: TAB / SPACE+								: drop
DEDENT		: !INDENT
CODECHAR	: [\x20..\x7f  \t]
DOCCHAR		: [\x20..\x7f  \t\n]
IDENTIFIER	: [a..z  A..Z  _] [a..z  A..Z  0..9  _]*	: join
#	lower-level patterns
funcName	: SPACING IDENTIFIER SPACING?				: liftValue
argument	: IDENTIFIER
codeLine	: INDENT? CODECHAR+ EOL						: join
#	func def
type		: COLON IDENTIFIER SPACING?					: liftValue
typeDef		: type?										: keep
moreArg		: COMMA SPACE* argument						: liftNode
argList		: LPAREN argument moreArg* RPAREN			: extract
arguments	: argList?									: keep
docBody		: INDENT* DOC (!DOC DOCCHAR)* DOC EOL?		: join
doc			: docBody?									: keep
codeBody	: INDENT codeLine+ DEDENT					: liftValue
code		: codeBody?									: keep
funcDef		: FUNCSTART funcName typeDef arguments EOL doc code FUNCEND

"""

from pijnu import *

### title: SebastienFunction ###
###   <toolset>
#	none

###   <definition>
#	simplified constants
SPACE = Char(' ', format="' '")(drop)
SPACING = Repetition(SPACE, numMin=1,numMax=False, format='SPACE+')(drop)
LPAREN = Char('(', format="'('")(drop)
RPAREN = Char(')', format="')'")(drop)
COMMA = Char(',', format="','")(drop)
DOC = Word("'''", format='"\\\'\\\'\\\'"')(drop)
FUNCSTART = Word('@function', format='"@function"')(drop)
FUNCEND = Word('@end', format='"@end"')(drop)
COLON = Char(':', format="':'")(drop)
EOL = Char('\n', format="'\\n'")(drop)
TAB = Char('\t', format="'\\t'")
INDENT = Choice([TAB, Repetition(SPACE, numMin=1,numMax=False, format='SPACE+')], format='TAB / SPACE+')(drop)
DEDENT = NextNot(INDENT, format='!INDENT')
CODECHAR = Klass(format='[\\x20..\\x7f  \\t]', charset=' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\t')
DOCCHAR = Klass(format='[\\x20..\\x7f  \\t\\n]', charset=' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\t\n')
IDENTIFIER = Sequence([Klass(format='[a..z  A..Z  _]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'), String(Klass(format='[a..z  A..Z  0..9  _]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'), numMin=False,numMax=False, format='[a..z  A..Z  0..9  _]*')], format='[a..z  A..Z  _] [a..z  A..Z  0..9  _]*')(join)
#	lower-level patterns
funcName = Sequence([SPACING, IDENTIFIER, Option(SPACING, format='SPACING?')], format='SPACING IDENTIFIER SPACING?')(liftValue)
argument = copy(IDENTIFIER)
codeLine = Sequence([Option(INDENT, format='INDENT?'), Repetition(CODECHAR, numMin=1,numMax=False, format='CODECHAR+'), EOL], format='INDENT? CODECHAR+ EOL')(join)
#	func def
type = Sequence([COLON, IDENTIFIER, Option(SPACING, format='SPACING?')], format='COLON IDENTIFIER SPACING?')(liftValue)
typeDef = Option(type, format='type?')(keep)
moreArg = Sequence([COMMA, Repetition(SPACE, numMin=False,numMax=False, format='SPACE*'), argument], format='COMMA SPACE* argument')(liftNode)
argList = Sequence([LPAREN, argument, Repetition(moreArg, numMin=False,numMax=False, format='moreArg*'), RPAREN], format='LPAREN argument moreArg* RPAREN')(extract)
arguments = Option(argList, format='argList?')(keep)
docBody = Sequence([Repetition(INDENT, numMin=False,numMax=False, format='INDENT*'), DOC, Repetition(Sequence([NextNot(DOC, format='!DOC'), DOCCHAR], format='!DOC DOCCHAR'), numMin=False,numMax=False, format='(!DOC DOCCHAR)*'), DOC, Option(EOL, format='EOL?')], format='INDENT* DOC (!DOC DOCCHAR)* DOC EOL?')(join)
doc = Option(docBody, format='docBody?')(keep)
codeBody = Sequence([INDENT, Repetition(codeLine, numMin=1,numMax=False, format='codeLine+'), DEDENT], format='INDENT codeLine+ DEDENT')(liftValue)
code = Option(codeBody, format='codeBody?')(keep)
funcDef = Sequence([FUNCSTART, funcName, typeDef, arguments, EOL, doc, code, FUNCEND], format='FUNCSTART funcName typeDef arguments EOL doc code FUNCEND')

SebastienFunctionParser = Parser(locals(), 'funcDef', 'SebastienFunction', 'SebastienFunction.py')

