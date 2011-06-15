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

"""
<definition>
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
grup = Recursive()
add = Recursive()
mult = Recursive()
digit = Klass(format='[0..9.]', charset='0123456789.')
number = Repetition(digit, numMin=1,numMax=False, format='digit+')(join, toReal)
ADD = Char('+', format="'+'")(drop)
MULT = Char('*', format="'*'")(drop)
LPAREN = Char('(', format="'('")(drop)
RPAREN = Char(')', format="')'")(drop)
mult **= Sequence([Choice([grup, number], format='grup/number'), MULT, Choice([grup, mult, number], format='grup/mult/number')], format='(grup/number) MULT (grup/mult/number)')
add **= Sequence([Choice([grup, mult, number], format='grup/mult/number'), ADD, Choice([grup, add, mult, number], format='grup/add/mult/number')], format='(grup/mult/number) ADD (grup/add/mult/number)')
grup **= Sequence([LPAREN, Choice([add, mult], format='add / mult'), RPAREN], format='LPAREN (add / mult) RPAREN')(liftNode)
formula = Choice([add, mult, digit], format='add / mult / digit')

formulaParser._recordPatterns(vars())
formulaParser._setTopPattern("formula")
formulaParser.grammarTitle = "formula"
formulaParser.fileName = "formulaParser.py"
