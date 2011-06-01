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
SEP			: ' '
DOT			: '.'
digit		: [0..9]
integer		: digit+
real		: integer DOT integer?
number		: real / integer
numbers		: number (SEP number)*


"""

from pijnu import *

### title: numbers ###
###   <toolset>
def doAddition(node):
	(n1,n2) = (node[0].value,node[1].value)
	node.value = int(n1) + int(n2)

###   <definition>
PLUS = Char('+')(drop)
digit = Klass(format='[0..9]', charset='0123456789')
integer = Repetition(digit, numMin=1,numMax=False, format='digit+')(join)
addition = Sequence([integer, PLUS, integer])(doAddition)

additionParser = Parser(vars(), 'addition', 'addition', 'None')

s = "22+333"
print additionParser.match(s)

