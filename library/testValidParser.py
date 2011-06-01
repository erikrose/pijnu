""" testValid
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
	x		: "x"		: noX
	letter	: [a..z]	: noX
	text	: letter{4..6}

"""



from pijnu.library import *

testValidParser = Parser()
state = testValidParser.state



### title: testValid ###
###   <toolset>
def noX(node):
	if node.value == 'x':
		message = "'x' is an invalid letter."
		(pattern,pos,source) = (node.pattern,node.start,node.source)
		raise Invalidation(message, pattern=pattern, source=source,pos=pos)

###   <definition>
x = Word('x', format='"x"')(noX)
letter = Klass(format='[a..z]', charset='abcdefghijklmnopqrstuvwxyz')(noX)
text = Repetition(letter, numMin=4,numMax=6, format='letter{4..6}')



testValidParser._recordPatterns(vars())
testValidParser._setTopPattern("text")
testValidParser.grammarTitle = "testValid"
testValidParser.fileName = "testValidParser.py"
