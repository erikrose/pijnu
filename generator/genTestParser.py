""" genTest
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
# constants
	SPACE		: ' '							: drop
	SPACING		: SPACE*						: drop
	DOT			: "."
	MINUS		: "-"
	PLUS		: "+"							: drop
	ADD			: PLUS
	_ADD_		: SPACING ADD SPACING			: drop
	MULT		: "*"
	_MULT_		: SPACING MULT SPACING			: drop
	DIGIT		: [0..9]
	SIGN		: PLUS / MINUS
	SIGN_		: SIGN SPACING
	LPAREN		: "("							: drop
	RPAREN		: ")"							: drop
	
# operand
	digits		: DIGIT+
	integer		: SIGN_? digits
	real		: integer (DOT digits)?
	number		: real / integer				: join toFloat
	group		: LPAREN operation RPAREN		: liftNode
	operand 	: group / number

# operation
	mult		: operand _MULT_ (mult/operand)	: @ doMult
	addOp		: mult / operand
	add			: addOp _ADD_  (add/addOp)		: @ doAdd
	operation	: add / mult					: @
	foo			: ("a"/"b"){3}
	bar			: [1..9]{3}
	baz			: '1'{3}
	result		: operation / operand			: formatResult

"""



from pijnu.library import *

genTestParser = Parser()
state = genTestParser.state



# a mini test grammar for the generator

### title: genTest ###


			   # foobar


###   <toolset>
def doMult(node):
	(a,b) = node
	node.value = a.value * b.value

def doAdd(node):
	(a,b) = node
	node.value = a.value + b.value
	
def formatResult(node):
	node.value = "%.3f" % node.value

###   <definition>
# recursive pattern(s)
operation = Recursive(name='operation')
add = Recursive(name='add')
mult = Recursive(name='mult')
# constants
SPACE = Char(' ', expression="' '",name='SPACE')(drop)
SPACING = Repetition(SPACE, numMin=False,numMax=False, expression='SPACE*',name='SPACING')(drop)
DOT = Word('.', expression='"."',name='DOT')
MINUS = Word('-', expression='"-"',name='MINUS')
PLUS = Word('+', expression='"+"',name='PLUS')(drop)
ADD = Clone(PLUS, expression='PLUS',name='ADD')
_ADD_ = Sequence([SPACING, ADD, SPACING], expression='SPACING ADD SPACING',name='_ADD_')(drop)
MULT = Word('*', expression='"*"',name='MULT')
_MULT_ = Sequence([SPACING, MULT, SPACING], expression='SPACING MULT SPACING',name='_MULT_')(drop)
DIGIT = Klass('0123456789', expression='[0..9]',name='DIGIT')
SIGN = Choice([PLUS, MINUS], expression='PLUS / MINUS',name='SIGN')
SIGN_ = Sequence([SIGN, SPACING], expression='SIGN SPACING',name='SIGN_')
LPAREN = Word('(', expression='"("',name='LPAREN')(drop)
RPAREN = Word(')', expression='")"',name='RPAREN')(drop)
	
# operand
digits = Repetition(DIGIT, numMin=1,numMax=False, expression='DIGIT+',name='digits')
integer = Sequence([Option(SIGN_, expression='SIGN_?'), digits], expression='SIGN_? digits',name='integer')
real = Sequence([integer, Option(Sequence([DOT, digits], expression='DOT digits'), expression='(DOT digits)?')], expression='integer (DOT digits)?',name='real')
number = Choice([real, integer], expression='real / integer',name='number')(join, toFloat)
group = Sequence([LPAREN, operation, RPAREN], expression='LPAREN operation RPAREN',name='group')(liftNode)
operand = Choice([group, number], expression='group / number',name='operand')

# operation
mult **= Sequence([operand, _MULT_, Choice([mult, operand], expression='mult/operand')], expression='operand _MULT_ (mult/operand)',name='mult')(doMult)
addOp = Choice([mult, operand], expression='mult / operand',name='addOp')
add **= Sequence([addOp, _ADD_, Choice([add, addOp], expression='add/addOp')], expression='addOp _ADD_  (add/addOp)',name='add')(doAdd)
operation **= Choice([add, mult], expression='add / mult',name='operation')
foo = Repetition(Choice([Word('a', expression='"a"'), Word('b', expression='"b"')], expression='"a"/"b"'), numMin=3,numMax=3, expression='("a"/"b"){3}',name='foo')
bar = Repetition(Klass('123456789', expression='[1..9]'), numMin=3,numMax=3, expression='[1..9]{3}',name='bar')
baz = Repetition(Char('1', expression="'1'"), numMin=3,numMax=3, expression="'1'{3}",name='baz')
result = Choice([operation, operand], expression='operation / operand',name='result')(formatResult)



genTestParser._recordPatterns(vars())
genTestParser._setTopPattern("result")
genTestParser.grammarTitle = "genTest"
genTestParser.filename = "genTestParser.py"
