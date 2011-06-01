"""
<definition>

''' © copyright 2009 Denis Derman
	contact: denis <dot> spir <at> free <dot> fr
	
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
{
# inline text
	lineChar		: [\x20..\xff]
	rawChar			: [\x20..\xff  !!/!_]
	DISTINCT		: "//"								: drop
	IMPORTANT		: "!!"								: drop
	MONOSPACE		: "__"								: drop
	rawText			: rawChar+							: join
	distinctText	: DISTINCT inline DISTINCT			: liftValue
	importantText	: IMPORTANT inline IMPORTANT		: liftValue
	monospaceText	: MONOSPACE inline MONOSPACE		: liftValue
	styledText		: distinctText / importantText / monospaceText
	text			: styledText / rawText
	inline			: text+								: @
# line types
	LF				: '
'
	CR				: ''
	EOL				: (LF/CR)+								: drop
	BULLETLIST		: "*"									: drop
	NUMBERLIST		: "#"									: drop
	TITLE			: "="									: drop
	paragraf		: !(BULLETLIST/NUMBERLIST) inline EOL	: liftValue
	paragrafs		: paragraf+
	bulletListItem	: BULLETLIST inline EOL					: liftValue
	bulletList		: bulletListItem+
	numberListItem	: NUMBERLIST inline EOL					: liftValue
	numberList		: numberListItem+
	blankLine		: EOL
	body			: (bulletList / numberList / paragrafs / blankLine)+
	#body			: (bulletListItem / numberListItem / paragraf / blankLine)+
	title			: TITLE inline EOL 					: liftValue
	text			: blankLine* title? body
}


"""

from pijnu import *

### title: wiki ###
### DEFINITION ###
# recursive pattern(s)
inline = Recursive()
# inline text
lineChar = Klass('[\\x20..\\xff]', ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff')
rawChar = Klass('[\\x20..\\xff  !!/!_]', ' "#$%&\'()*+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^`abcdefghijklmnopqrstuvwxyz{|}~\x7f\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff')
DISTINCT = Word('//')(drop)
IMPORTANT = Word('!!')(drop)
MONOSPACE = Word('__')(drop)
rawText = OneOrMore(rawChar)(join)
distinctText = Sequence(DISTINCT, inline, DISTINCT)(liftValue)
importantText = Sequence(IMPORTANT, inline, IMPORTANT)(liftValue)
monospaceText = Sequence(MONOSPACE, inline, MONOSPACE)(liftValue)
styledText = Choice(distinctText, importantText, monospaceText)
text = Choice(styledText, rawText)
inline **= OneOrMore(text)
# line types
LF = Char('\n')
CR = Char('\r')
EOL = OneOrMore(Choice(LF, CR))(drop)
BULLETLIST = Word('*')(drop)
NUMBERLIST = Word('#')(drop)
TITLE = Word('=')(drop)
paragraf = Sequence(NextNot(Choice(BULLETLIST, NUMBERLIST)), inline, EOL)(liftValue)
paragrafs = OneOrMore(paragraf)
bulletListItem = Sequence(BULLETLIST, inline, EOL)(liftValue)
bulletList = OneOrMore(bulletListItem)
numberListItem = Sequence(NUMBERLIST, inline, EOL)(liftValue)
numberList = OneOrMore(numberListItem)
blankLine = copy(EOL)
body = OneOrMore(Choice(bulletList, numberList, paragrafs, blankLine))
#	body			: (bulletListItem / numberListItem / paragraf / blankLine)+
title = Sequence(TITLE, inline, EOL)(liftValue)
text = Sequence(ZeroOrMore(blankLine), Option(title), body)


wikiParser = Parser(locals(), 'text', 'wiki', 'wiki.py')

