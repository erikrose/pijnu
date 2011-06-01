""" addition
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
SEP			: ' '						: drop
DOT			: '.'
digit		: [0..9]
integer		: digit+					: join
real		: integer DOT integer?		: join
number		: real / integer			: toReal
addedNum	: SEP number				: liftNode
numbers		: number (addedNum)*		: extract

"""



from pijnu.library import *

additionParser = Parser()
state = additionParser.state



### title: addition ###


###   <toolset>
def doAdd(node):
    (n1,n2) = (node[0].value,node[1].value)
    node.value = int(n1) + int(n2)

###   <definition>
# constants
SEP = Char(' ', expression="' '",name='SEP')(drop)
ADD = Char('+', name='ADD')(drop)
# operand
digit = Klass('0123456789', expression='[0..9]',name='digit')
integer = Repetition(digit, numMin=1,numMax=False, expression='digit+',name='integer')(join)
# operation
addition = Sequence([integer, ADD, integer], name="addition")#(doAdd)



additionParser._recordPatterns(vars())
additionParser._setTopPattern("addition")
additionParser.grammarTitle = "addition"
additionParser.filename = "additionParser.py"
