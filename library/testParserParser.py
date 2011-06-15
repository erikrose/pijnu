""" testParser
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
	w1 : "foo"
	w2 : "bar"
	ch : w1 / w2

"""



from pijnu.library import *

testParserParser = Parser()
state = testParserParser.state




### title: testParser ###


###   <definition>
w1 = Word('foo', expression='"foo"',name='w1')
w2 = Word('bar', expression='"bar"',name='w2')
ch = Choice([w1, w2], expression='w1 / w2',name='ch')



testParserParser._recordPatterns(vars())
testParserParser._setTopPattern("ch")
testParserParser.grammarTitle = "testParser"
testParserParser.filename = "testParserParser.py"
