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
# tokens
	EOL		    : [
]+			    : drop
	SPACING	    : [ 	]+				: drop
	EQ_CODE	    : SPACING "=" SPACING   : drop
	CH_CODE	    : SPACING "|" SPACING   : drop
	DIGIT	    : [0..9]
	number	    : DIGIT+				: join integer
	LETTER	    : [a..z  A..Z]
	variable	: LETTER+               : join
# operation
	eq_operand  : variable / number
	equality	: eq_operand EQ_CODE eq_operand
	ch_operand  : equality / variable
	choice	    : ch_operand CH_CODE ch_operand
	operation   : (choice / equality / variable) EOL : liftNode

"""

from pijnu import *

### title: miniLogic ###
###   <toolset>
def integer(node):
	''' Convert node value to python int. '''
	node.value = int(node.value)

###   <definition>
# tokens
EOL = String(Klass(format='[\n\r]', charset='\n\r'), numMin=1,numMax=False, format='[\n\r]+')(drop)
SPACING = String(Klass(format='[ \t]', charset=' \t'), numMin=1,numMax=False, format='[ \t]+')(drop)
EQ_CODE = Sequence([SPACING, Word('=', format='"="'), SPACING], format='SPACING "=" SPACING')(drop)
CH_CODE = Sequence([SPACING, Word('|', format='"|"'), SPACING], format='SPACING "|" SPACING')(drop)
DIGIT = Klass(format='[0..9]', charset='0123456789')
number = Repetition(DIGIT, numMin=1,numMax=False, format='DIGIT+')(join, integer)
LETTER = Klass(format='[a..z  A..Z]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
variable = Repetition(LETTER, numMin=1,numMax=False, format='LETTER+')(join)
# operation
eq_operand = Choice([variable, number], format='variable / number')
equality = Sequence([eq_operand, EQ_CODE, eq_operand], format='eq_operand EQ_CODE eq_operand')
ch_operand = Choice([equality, variable], format='equality / variable')
choice = Sequence([ch_operand, CH_CODE, ch_operand], format='ch_operand CH_CODE ch_operand')
operation = Sequence([Choice([choice, equality, variable], format='choice / equality / variable'), EOL], format='(choice / equality / variable) EOL')(liftNode)

miniLogicParser = Parser(vars(), 'operation', 'miniLogic', 'None')

