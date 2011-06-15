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

"""		wikiLine
	lineChar		: [\x20..\x7e]
	rawChar			: [\x20..\x7e  !!/!_]
	DISTINCT		: "//"								: drop
	IMPORTANT		: "!!"								: drop
	MONOSPACE		: "__"								: drop
	rawText			: rawChar+							: join
	distinctText	: DISTINCT inline DISTINCT			: liftValue
	importantText	: IMPORTANT inline IMPORTANT		: liftValue
	monospaceText	: MONOSPACE inline MONOSPACE		: liftValue
	styledText		: distinctText / importantText / monospaceText
	text			: styledText / rawText
	inline			: @ text+

"""

from pijnu import *

# title: wikiLine
inline = Recursion()
lineChar = Klass(' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')
rawChar = Klass(' "#$%&\'()*+,-.0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^`abcdefghijklmnopqrstuvwxyz{|}~  ')
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

parser = Parser('wikiLine', locals(), 'inline')
