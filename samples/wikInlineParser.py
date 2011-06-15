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
# codes
	ESCAPE			: '~'
	DISTINCT		: "//"									: drop
	IMPORTANT		: "!!"									: drop
	WARNING			: "**"									: drop
	styleCode		: (DISTINCT / IMPORTANT / WARNING)
# character expression
	escChar			: ESCAPE ('*' / '!' / '/' / ESCAPE)		: unescape
	validChar		: [\x20..\xff  !!/!*~]
	rawText			: (escChar / (!styleCode validChar))+	: join
# text kinds
	distinctText	: DISTINCT inlineText DISTINCT			: liftValue
	importantText	: IMPORTANT inlineText IMPORTANT		: liftValue
	warningText		: WARNING inlineText WARNING			: liftValue
	styledText		: distinctText / importantText / warningText	: styledSpan
	inlineText		: (styledText / rawText)+				: @ join

"""

from pijnu import *

### title: wikInline ###
###   <toolset>
def unescape(node):
	node.value = node[1].value
def styledSpan(node):
	klass = node.tag
	text = node.value
	node.value = '<span class="%s">%s</span>' %(klass,text)

# recursive pattern(s)

inlineText = Recursive()

###   <definition>
# codes
ESCAPE = Char('~', format="'~'")
DISTINCT = Word('//', format='"//"')(drop)
IMPORTANT = Word('!!', format='"!!"')(drop)
WARNING = Word('**', format='"**"')(drop)
styleCode = Choice([DISTINCT, IMPORTANT, WARNING], format='DISTINCT / IMPORTANT / WARNING')
# character expression
escChar = Sequence([ESCAPE, Choice([Char('*', format="'*'"), Char('!', format="'!'"), Char('/', format="'/'"), ESCAPE], format="'*' / '!' / '/' / ESCAPE")], format="ESCAPE ('*' / '!' / '/' / ESCAPE)")(unescape)
validChar = Klass(format='[\\x20..\\xff  !!/!*~]', charset=' "#$%&\'()+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff')
rawText = Repetition(Choice([escChar, Sequence([NextNot(styleCode, format='!styleCode'), validChar], format='!styleCode validChar')], format='escChar / (!styleCode validChar)'), numMin=1,numMax=False, format='(escChar / (!styleCode validChar))+')(join)
# text kinds
distinctText = Sequence([DISTINCT, inlineText, DISTINCT], format='DISTINCT inlineText DISTINCT')(liftValue)
importantText = Sequence([IMPORTANT, inlineText, IMPORTANT], format='IMPORTANT inlineText IMPORTANT')(liftValue)
warningText = Sequence([WARNING, inlineText, WARNING], format='WARNING inlineText WARNING')(liftValue)
styledText = Choice([distinctText, importantText, warningText], format='distinctText / importantText / warningText')(styledSpan)
inlineText **= Repetition(Choice([styledText, rawText], format='styledText / rawText'), numMin=1,numMax=False, format='(styledText / rawText)+')(join)

wikInlineParser = Parser(vars(), 'inlineText', 'wikInline', 'None')
