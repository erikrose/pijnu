""" standardDiff
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
# tokens
	# separators
		### Note: DROP_* versions are for pattern definition lines.
		# end of line
		EOL				: '\n'
		DROP_EOL		: '\n'								: drop
		# blank spacing
		SPACE			: ' '
		TAB				: '\t'
		BLANK			: (TAB / SPACE)*
		DROP_BLANK		: (TAB / SPACE)*					: drop
		# comment mark
		COMMENT			: "#"
		# colon "assignment"
		COLON			: ":"
		ASSIGN			: DROP_BLANK COLON DROP_BLANK		: drop
		# start of section
		DEFINITION		: "<definition>"
		TOOLSET			: "<toolset>"
		DEF_START		: DEFINITION EOL					: drop
	# character classes & strings
		# name
		NAME_START_CHAR	: [_  a..z  A..Z]
		NAME_SUITE_CHAR	: [_  a..z  A..Z  0..9]
		name			: NAME_START_CHAR NAME_SUITE_CHAR+	: join
		# inline (LATIN-only for test)
		INLINE_CHAR		: [ \t  \x21..\x7e  \xa0..\xff]
		inline			: INLINE_CHAR*						: join
# structure
	# skipped line types
		blankLine		: BLANK  EOL
		commentLine		: BLANK  COMMENT inline EOL
		skipLine		: blankLine / commentLine			: join
	# header section
		titleLine		: BLANK name EOL					: setTitle
		header			: skipLine* titleLine skipLine*		: join
	# toolset section
		toolStartLine	: BLANK TOOLSET EOL
		toolsetLine		: !DEFINITION inline EOL
		toolset			: toolStartLine toolsetLine+		: join
	# definition section
		defStartLine	: BLANK DEFINITION EOL				: join
		patDefLine		: DROP_BLANK name ASSIGN inline DROP_EOL: updatePattern
		defBLock		: (patDefLine / skipLine)+
		definition		: defStartLine defBLock				: listPatterns join
	# whole grammar
		grammar			: header toolset definition			: join

"""



from pijnu.library import *

standardDiffParser = Parser()
state = standardDiffParser.state



# Parse standard booleano grammar to update it
# from pattern definitions read from differential config.
# Actually, we could only find & process pattern definition lines,
# because their pattern makes no possible ambiguity.
# But: to rewrite the modified grammar, we need to
# parse & record its content and structure as well.

### title: standardDiff ###
###   <toolset>
from pijnu.generator import writeParser
# get differential config dict
def getDiffDict():
	# (first rewrite configParser for test)
	config_grammar = file("config.pijnu").read()
	writeParser(config_grammar)
	# Use configParser's findAll method
	# to get pattern list from lang config.
	from configParser import configParser
	currentConfig = file("currentConfig.pijnu").read()
	patterns = configParser.findAll(currentConfig)
	#~print "=== diff patterns ==="
	#~for pattern in patterns:
	#~	print pattern
	# Build pattern dict.
	diff_dict = {}
	for pattern in patterns:
		(name,defin) = pattern
		diff_dict[name.value] = defin.value
	return diff_dict
diff_dict = getDiffDict()
def updatePattern(node):
	''' Update pattern definition from diff config dict
		-- if ever this dict holds a pattern of same name.
		And simply rewrite it... '''
	(name,defin) = (node[0].value,node[1].value)
	if name in diff_dict:
		defin = diff_dict[name]
	node.value = "%s : %s\n" %(name,defin)
	# that's all, folks!
def listPatterns(node):
	''' List possibly updated pattern definitions. '''
	return
	print "=== pattern definitions ==="
	for line in node:
		if line.typ == "patDefLine":
			print line
def setTitle(node):
	''' Set title "lang" so that
		* it is not called 'standard'
		* we know how the parser will be called. '''
	node.value = "lang\n"

###   <definition>
# tokens
	# separators
		### Note: DROP_* versions are for pattern definition lines.
		# end of line
EOL = Char('\n', format="'\\n'")
DROP_EOL = Char('\n', format="'\\n'")(drop)
		# blank spacing
SPACE = Char(' ', format="' '")
TAB = Char('\t', format="'\\t'")
BLANK = Repetition(Choice([TAB, SPACE], format='TAB / SPACE'), numMin=False,numMax=False, format='(TAB / SPACE)*')
DROP_BLANK = Repetition(Choice([TAB, SPACE], format='TAB / SPACE'), numMin=False,numMax=False, format='(TAB / SPACE)*')(drop)
		# comment mark
COMMENT = Word('#', format='"#"')
		# colon "assignment"
COLON = Word(':', format='":"')
ASSIGN = Sequence([DROP_BLANK, COLON, DROP_BLANK], format='DROP_BLANK COLON DROP_BLANK')(drop)
		# start of section
DEFINITION = Word('<definition>', format='"<definition>"')
TOOLSET = Word('<toolset>', format='"<toolset>"')
DEF_START = Sequence([DEFINITION, EOL], format='DEFINITION EOL')(drop)
	# character classes & strings
		# name
NAME_START_CHAR = Klass(format='[_  a..z  A..Z]', charset='_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
NAME_SUITE_CHAR = Klass(format='[_  a..z  A..Z  0..9]', charset='_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
name = Sequence([NAME_START_CHAR, Repetition(NAME_SUITE_CHAR, numMin=1,numMax=False, format='NAME_SUITE_CHAR+')], format='NAME_START_CHAR NAME_SUITE_CHAR+')(join)
		# inline (LATIN-only for test)
INLINE_CHAR = Klass(format='[ \\t  \\x21..\\x7e  \\xa0..\\xff]', charset=' \t!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff')
inline = Repetition(INLINE_CHAR, numMin=False,numMax=False, format='INLINE_CHAR*')(join)
# structure
	# skipped line types
blankLine = Sequence([BLANK, EOL], format='BLANK  EOL')
commentLine = Sequence([BLANK, COMMENT, inline, EOL], format='BLANK  COMMENT inline EOL')
skipLine = Choice([blankLine, commentLine], format='blankLine / commentLine')(join)
	# header section
titleLine = Sequence([BLANK, name, EOL], format='BLANK name EOL')(setTitle)
header = Sequence([Repetition(skipLine, numMin=False,numMax=False, format='skipLine*'), titleLine, Repetition(skipLine, numMin=False,numMax=False, format='skipLine*')], format='skipLine* titleLine skipLine*')(join)
	# toolset section
toolStartLine = Sequence([BLANK, TOOLSET, EOL], format='BLANK TOOLSET EOL')
toolsetLine = Sequence([NextNot(DEFINITION, format='!DEFINITION'), inline, EOL], format='!DEFINITION inline EOL')
toolset = Sequence([toolStartLine, Repetition(toolsetLine, numMin=1,numMax=False, format='toolsetLine+')], format='toolStartLine toolsetLine+')(join)
	# definition section
defStartLine = Sequence([BLANK, DEFINITION, EOL], format='BLANK DEFINITION EOL')(join)
patDefLine = Sequence([DROP_BLANK, name, ASSIGN, inline, DROP_EOL], format='DROP_BLANK name ASSIGN inline DROP_EOL')(updatePattern)
defBLock = Repetition(Choice([patDefLine, skipLine], format='patDefLine / skipLine'), numMin=1,numMax=False, format='(patDefLine / skipLine)+')
definition = Sequence([defStartLine, defBLock], format='defStartLine defBLock')(listPatterns, join)
	# whole grammar
grammar = Sequence([header, toolset, definition], format='header toolset definition')(join)



standardDiffParser._recordPatterns(vars())
standardDiffParser._setTopPattern("grammar")
standardDiffParser.grammarTitle = "standardDiff"
standardDiffParser.filename = "standardDiffParser.py"
