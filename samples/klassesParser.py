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
# coding
	LBRACKET	: '['										: drop
	RBRACKET	: '\]'										: drop
	SEP			: "  "										: drop
	EXCLUSION	: "!!"										: drop
	RANGE		: ".."										: drop
	ESC			: "\\"										: drop
	DEC			: "\\"										: drop
	HEX			: "\\x"										: drop
	DECNUM		: [0..9]
	HEXNUM		: [0..9  a..eA..E]
# character expression
	safeChar	: !EXCLUSION [\x20..\x7e  !!\]]				: liftNode
	escChar		: ESC '\]'									: charFromEsc
	decChar		: DEC DECNUM{3}								: join charFromDec
	hexChar		: HEX HEXNUM{2}								: join charFromHex
	char		: hexChar / decChar / escChar / safeChar
# klass format
	ranj		: char RANGE char							: charsetFromRanj
	klassItem	: SEP / ranj / char
	charset		: klassItem+								: join
	exclCharset	: charset EXCLUSION charset					: excludedCharset
	klass		: LBRACKET (exclCharset / charset) RBRACKET	: liftValue

"""

from pijnu import *

### title: klasses ###
###   <toolset>
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

###   <definition>
# coding
LBRACKET = Char('[', format="'['")(drop)
RBRACKET = Char(']', format="'\\]'")(drop)
SEP = Word('  ', format='"  "')(drop)
EXCLUSION = Word('!!', format='"!!"')(drop)
RANGE = Word('..', format='".."')(drop)
ESC = Word('\\', format='"\\\\"')(drop)
DEC = Word('\\', format='"\\\\"')(drop)
HEX = Word('\\x', format='"\\\\x"')(drop)
DECNUM = Klass(format='[0..9]', charset='0123456789')
HEXNUM = Klass(format='[0..9  a..eA..E]', charset='0123456789abcdeABCDE')
# character expression
safeChar = Sequence([NextNot(EXCLUSION, format='!EXCLUSION'), Klass(format='[\\x20..\\x7e  !!\\]]', charset=' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\^_`abcdefghijklmnopqrstuvwxyz{|}~')], format='!EXCLUSION [\\x20..\\x7e  !!\\]]')(liftNode)
escChar = Sequence([ESC, Char(']', format="'\\]'")], format="ESC '\\]'")(charFromEsc)
decChar = Sequence([DEC, Repetition(DECNUM, numMin=3,numMax=3, format='DECNUM{3}')], format='DEC DECNUM{3}')(join, charFromDec)
hexChar = Sequence([HEX, Repetition(HEXNUM, numMin=2,numMax=2, format='HEXNUM{2}')], format='HEX HEXNUM{2}')(join, charFromHex)
char = Choice([hexChar, decChar, escChar, safeChar], format='hexChar / decChar / escChar / safeChar')
# klass format
ranj = Sequence([char, RANGE, char], format='char RANGE char')(charsetFromRanj)
klassItem = Choice([SEP, ranj, char], format='SEP / ranj / char')
charset = Repetition(klassItem, numMin=1,numMax=False, format='klassItem+')(join)
exclCharset = Sequence([charset, EXCLUSION, charset], format='charset EXCLUSION charset')(excludedCharset)
klass = Sequence([LBRACKET, Choice([exclCharset, charset], format='exclCharset / charset'), RBRACKET], format='LBRACKET (exclCharset / charset) RBRACKET')(liftValue)

klassesParser = Parser(vars(), 'klass', 'klasses', 'None')
