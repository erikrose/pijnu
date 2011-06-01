""" formula
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
digit		: [0..9.]
number		: digit+										: join toReal
ADD			: '+'											: drop
MULT		: '*'											: drop
LPAREN		: '('											: drop
RPAREN		: ')'											: drop
mult		: (grup/number) MULT (grup/mult/number)			: @
add			: (grup/mult/number) ADD (grup/add/mult/number) : @
grup		: LPAREN (add / mult) RPAREN					: @ liftNode
formula		: add / mult / digit

"""



from pijnu.library import *

formulaParser = Parser()
state = formulaParser.state



### title: formula ###


###   <toolset>
def doAdd(node):
	(n1,n2) = (node[0].value,node[1].value)
	node.value = n1 + n2
def doMult(node):
	(n1,n2) = (node[0].value,node[1].value)
	node.value = n1 * n2

###   <definition>
# recursive pattern(s)
grup = Recursive(name='grup')
add = Recursive(name='add')
mult = Recursive(name='mult')
digit = Klass('0123456789.', expression='[0..9.]',name='digit')
number = Repetition(digit, numMin=1,numMax=False, expression='digit+',name='number')(join, toReal)
ADD = Char('+', expression="'+'",name='ADD')(drop)
MULT = Char('*', expression="'*'",name='MULT')(drop)
LPAREN = Char('(', expression="'('",name='LPAREN')(drop)
RPAREN = Char(')', expression="')'",name='RPAREN')(drop)
mult **= Sequence([Choice([grup, number], expression='grup/number'), MULT, Choice([grup, mult, number], expression='grup/mult/number')], expression='(grup/number) MULT (grup/mult/number)',name='mult')
add **= Sequence([Choice([grup, mult, number], expression='grup/mult/number'), ADD, Choice([grup, add, mult, number], expression='grup/add/mult/number')], expression='(grup/mult/number) ADD (grup/add/mult/number)',name='add')
grup **= Sequence([LPAREN, Choice([add, mult], expression='add / mult'), RPAREN], expression='LPAREN (add / mult) RPAREN',name='grup')(liftNode)
formula = Choice([add, mult, digit], expression='add / mult / digit',name='formula')



formulaParser._recordPatterns(vars())
formulaParser._setTopPattern("formula")
formulaParser.grammarTitle = "formula"
formulaParser.filename = "formulaParser.py"
