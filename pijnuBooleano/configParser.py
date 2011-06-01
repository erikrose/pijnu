""" config
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
# separators
	### Note: DROP_* versions are for pattern definition lines.
	# end of line
	EOL				: '\n'									: drop
	# blank spacing
	SPACE			: ' '
	TAB				: '\t'
	BLANK			: (TAB / SPACE)*						: drop
	# colon "assignment"
	COLON			: ":"
	ASSIGN			: BLANK COLON BLANK					: drop
# character classes & strings
	# name
	NAME_START_CHAR	: [_  a..z  A..Z]
	NAME_SUITE_CHAR	: [_  a..z  A..Z  0..9]
	name			: NAME_START_CHAR NAME_SUITE_CHAR+		: join
	# inline (LATIN-only for test)
	INLINE_CHAR		: [ \t  \x21..\x7e  \xa0..\xff]
	inline			: INLINE_CHAR+							: join
# pattern definition line
	patDefLine		: BLANK name ASSIGN inline EOL			: showPattern

"""



from pijnu.library import *

configParser = Parser()
state = configParser.state



### TODO ###
# Parse differential config file to store
# pattern definitions in a dict of {name:patDef} pairs.
# We need only findAll pattern definition lines, actually.

### title: config ###
###   <toolset>
def showPattern(node):
	#~print "*** config pattern:", node
	pass

###   <definition>
# separators
	### Note: DROP_* versions are for pattern definition lines.
	# end of line
EOL = Char('\n', format="'\\n'")(drop)
	# blank spacing
SPACE = Char(' ', format="' '")
TAB = Char('\t', format="'\\t'")
BLANK = Repetition(Choice([TAB, SPACE], format='TAB / SPACE'), numMin=False,numMax=False, format='(TAB / SPACE)*')(drop)
	# colon "assignment"
COLON = Word(':', format='":"')
ASSIGN = Sequence([BLANK, COLON, BLANK], format='BLANK COLON BLANK')(drop)
# character classes & strings
	# name
NAME_START_CHAR = Klass(format='[_  a..z  A..Z]', charset='_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
NAME_SUITE_CHAR = Klass(format='[_  a..z  A..Z  0..9]', charset='_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
name = Sequence([NAME_START_CHAR, Repetition(NAME_SUITE_CHAR, numMin=1,numMax=False, format='NAME_SUITE_CHAR+')], format='NAME_START_CHAR NAME_SUITE_CHAR+')(join)
	# inline (LATIN-only for test)
INLINE_CHAR = Klass(format='[ \\t  \\x21..\\x7e  \\xa0..\\xff]', charset=' \t!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff')
inline = Repetition(INLINE_CHAR, numMin=1,numMax=False, format='INLINE_CHAR+')(join)
# pattern definition line
patDefLine = Sequence([BLANK, name, ASSIGN, inline, EOL], format='BLANK name ASSIGN inline EOL')(showPattern)



configParser._recordPatterns(vars())
configParser._setTopPattern("patDefLine")
configParser.grammarTitle = "config"
configParser.filename = "configParser.py"
