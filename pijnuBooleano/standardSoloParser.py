""" standardSolo
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

### tokens
	# StandardConfig tokens
		### Note: changed MEMBER and SUBSET as of now (unicode issue).
		# Logical connectives
		NOT 				: "~"					: drop
		AND 				: "&"					: drop
		OR 					: "|"					: drop
		XOR 				: "^"					: drop
		# Relational operators
		EQ			 		: "=="					: drop
		NE 					: "!="					: drop
		LT 					: "<"					: drop
		GT 					: ">"					: drop
		LE 					: "<="					: drop
		GE 					: ">="					: drop
		# Set operators
		MEMBER 				: "MEMBER"				: drop
		SUBSET		 		: "SUBSET"				: drop
		SET_START 			: "{"					: drop
		SET_END				: "}"					: drop
		ELEMENT_SEPARATOR	: ","					: drop
		# Grouping marks
		GROUP_START		 	: "("					: drop
		GROUP_END 			: ")"					: drop
		### Do not drop string delimiters to allow doubling.
		STRING_START 		: "\""					: 
		STRING_END 			: "\""					: 
		# Token internal characters
		DECIMAL_SEPARATOR	: '.'					: drop
		### Do not drop integer sep & ID spacing !
		INTEGER_SEPARATOR	: ','					: 
		ID_SPACING 			: '_'					: 
		# minus sign
		MINUS			: "-"
	# spacing & separation
		SPACING			: [\t ]+					: drop
		OPT_SPC			: [\t ]*					: drop
		SET_SEP			: OPT_SPC ELEMENT_SEPARATOR OPT_SPC	: drop
	# operators with spacing -- derived from standard config
		MINUS_			: "-" OPT_SPC
		# Logical connectives
		NOT_			: NOT OPT_SPC				: drop
		_AND_ 			: OPT_SPC AND OPT_SPC		: drop
		_OR_ 			: OPT_SPC OR OPT_SPC		: drop
		_XOR_ 			: OPT_SPC XOR OPT_SPC		: drop
		# Relational operators
		_EQ_			: OPT_SPC EQ OPT_SPC		: drop
		_NE_ 			: OPT_SPC NE OPT_SPC		: drop
		_LT_ 			: OPT_SPC LT OPT_SPC		: drop
		_GT_ 			: OPT_SPC GT OPT_SPC		: drop
		_LE_ 			: OPT_SPC LE OPT_SPC		: drop
		_GE_ 			: OPT_SPC GE OPT_SPC		: drop
		_MEMBER_		: OPT_SPC "MEMBER" OPT_SPC	: drop
		_SUBSET_ 		: OPT_SPC "SUBSET" OPT_SPC	: drop
	# character classes
		DIGIT			: [0..9]
		ID_SPECIFIC_CHAR: [a..z  A..Z] / ID_SPACING
		ID_SUITE_CHAR	: [a..z  A..Z  0..9] / ID_SPACING
		# Double (end) string delimiter to escape it.
		# Other characters are all safe
		DBL_STRING_END	: STRING_END STRING_END		: simpleStringEnd
		# String character class limited to inline ASCII for test.
		SAFE_STRING_CHAR: !STRING_END [ \t  \x21..\x7e]
		STRING_CHAR		: DBL_STRING_END / SAFE_STRING_CHAR

# operands
	# These are base operands for operations that yield truth values:
	# namely comparisons and set operations.
	# Logical operations instead take *and* return truth values.
	### @@@ operand is recursive because of sets @@@
	# number
		#   INTEGER_GROUPING_NUMBER is checked in validation.
		digits			: DIGIT+								: join
		integral_part	: (DIGIT / INTEGER_SEPARATOR)+			: join validateInt
		fractional_part	: DECIMAL_SEPARATOR digits				: join
		integer			: MINUS_? integral_part					: join
		real			: integer fractional_part				: writeReal
		number			: real / integer						: toNumber
	# string
		stringChars		: STRING_CHAR*							: join
		string			: STRING_START stringChars STRING_END	: toString
	# set
		### Note: Set must be frozen to allow nesting!
		elements		: operand (SET_SEP operand)*			: intoList
		set_			: SET_START elements SET_END			: liftValue toSet
	# ID
		### Note: as of now did not follow the rule that
		#   ID names may start with digit.
		ID				: DIGIT* ID_SPECIFIC_CHAR ID_SUITE_CHAR*: join getVar
	# any kind of operand
		### @@@ pattern operand is recursive into set_ element @@@
		### Note: Shouldn't operand allow group?
		### Note: number must be matched after ID to avoid confusion
		#		 with IDs starting with one or more digit(s)
		operand			: set_ / string / ID / number			: @

# operations
	# comparison: takes base operands, yield logic value
		eqComp			: operand _EQ_ operand					: toEQ
		neComp			: operand _NE_ operand					: toNE
		gtComp			: operand _GT_ operand					: toGT
		ltComp			: operand _LT_ operand					: toLT
		geComp			: operand _GE_ operand					: toGE
		leComp			: operand _LE_ operand					: toLE
		comparison		: eqComp / neComp / ltComp / gtComp / leComp / geComp
	# set operation: takes specific operands, yields logic value
		memberOperation	: operand _MEMBER_ set_					: toMEMBER
		subsetOperation	: set_ _SUBSET_ set_					: toSUBSET
		setOperation	: memberOperation / subsetOperation
	# logic operation: takes logic operand(s), yields logic value
		notOperand		: group / setOperation / comparison
		notOperation	: NOT_ notOperand						: toNOT
		andOperand		: notOperation / notOperand
		andOperation	: andOperand _AND_ andOperand			: toAND
		orOperand		: andOperation / andOperand
		orOperation		: orOperand _OR_ orOperand				: toOR
		xorOperation	: orOperand _XOR_ orOperand				: toXOR
		logicOperation	: xorOperation / orOperation / andOperation / notOperation
	# group from operation (all return logical value)
		operation		: logicOperation / setOperation / comparison
		group			: GROUP_START operation GROUP_END		: @ liftNode
		### anyOperand just for test funcs:
		anyOperand		: operand / group
	result			: operation / operand / group

# assignment -- just for fun
	_ASSIGNMENT_	: OPT_SPC ":" OPT_SPC					: drop
	name			: ID_SPECIFIC_CHAR ID_SUITE_CHAR*		: join
	value			: operation / operand
	assignment		: name _ASSIGNMENT_ result				: setVar

"""



from pijnu.library import *

standardSoloParser = Parser()
state = standardSoloParser.state



### title: standardSolo ###
###   <toolset>
### booleano node types
import sys
sys.path.append("/home/spir/pijnu/pijnuBooleano/booleano")
from booleano.operations import (
		# Operands:
		String as BooString, Number as BooNumber, Set as BooSet,
		Variable as BooVariable, Function as BooFunction,
		VariablePlaceholder,FunctionPlaceholder,
		# Operators:
		Truth,Not,And,Or,Xor,Equal,NotEqual,LessThan,
		GreaterThan,LessEqual,GreaterEqual,Contains,IsSubset,
		)
### operands
# number
T_INTEGER_SEPARATOR = ","
INTEGER_GROUPING_NUMBER = 3
def validateInt(node):
	''' Validate integral part format:
		possible INTEGER_SEPARATOR-s must be placed
		correctly, according to INTEGER_GROUPING_NUMBER '''
	# collect separator positions
	# -- counting from the end
	string = node.value
	char_count = len(string)
	sep_pos = []
	for (pos,char) in enumerate(string):
		if char == T_INTEGER_SEPARATOR:
			sep_pos.append(char_count - pos)
	sep_count = len(sep_pos)
	if sep_count == 0: return
	# check separator positions
	offset = INTEGER_GROUPING_NUMBER + 1
	expected_pos = [offset*(i+1) for i in range(sep_count)]
	expected_pos = list(reversed(expected_pos))
	if sep_pos != expected_pos:
		message = (	"Invalid format of integral part:\n"
					"separator(s) placed at wrong position.\n"
					"   %s" % node )
		raise Invalidation(message)
	# remove separators:
	node.value = node.value.replace(T_INTEGER_SEPARATOR, "")
def writeReal(node):
	''' Write expression of real number from integral and fractional parts. '''
	(int_part,fract_part) = (node[0].value,node[1].value)
	node.value = "%s.%s" %(int_part,fract_part) 
def toNumber(node):
	''' Convert expression of number to Booleano Number. '''
	node.value = BooNumber(node.value)
# string
def simpleStringEnd(node):
	''' Replace doubled string end to simple literal. '''
	# This will allow eg "a""b" --> String('a"b')
	node.value = node[0].value
def toString(node):
	''' Convert expression of string to Booleano String. '''
	node.value = BooString(node[1].value)
# set
def toSet(node):
	''' Convert expression of set to Booleano Set. '''
	items = [item.value for item in node]
	node.value = BooSet(*items)
# identifier operands
class MockID(BooString):
	''' placeholder for a booleano IDentifier operand
		More or less behaves like a named string operand.
		'''
	def __init__(self, name, value=""):
		self.name = name
		self.value = BooString(value)
	def equals(self, value, **helpers):
		value = unicode(value)
		return super(String, self.value).equals(value, **helpers)
	def __getattr__(self, attr_name):
		return getattr(self.value, attr_name)
	def __repr__(self):
		return "<ID %s:%s>" %(self.name,self.value)
def getVar(node):
	''' (Try to) get value for ID from parser state.
		Else create a ID placeholder. '''
	name = node.value
	try:
		value = getattr(state, name)
		node.value = value
	except AttributeError:
		node.value = MockID(name)
def setVar(node):
	''' Record ID name & value as parser state attribute. '''
	(name,value) = (node[0].value,node[1].value)
	setattr(state, name, value)
### operations
# comparisons
def toEQ(node):
	''' Convert expression of == operation to Booleano Equal. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = Equal(a, b)
def toNE(node):
	''' Convert expression of != operation to Booleano NotEqual. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = NotEqual(a, b)
def toLT(node):
	''' Convert expression of != operation to Booleano LessThan. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = LessThan(a, b)
def toGT(node):
	''' Convert expression of != operation to Booleano GreaterThan. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = GreaterThan(a, b)
def toLE(node):
	''' Convert expression of != operation to Booleano LessEqual. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = LessEqual(a, b)
def toGE(node):
	''' Convert expression of != operation to Booleano GreaterEqual. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = GreaterEqual(a, b)
# set operations
def toMEMBER(node):
	''' Convert expression of membership operation to Booleano Contains. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = Contains(a, b)
def toSUBSET(node):
	''' Convert expression of subset operation to Booleano IsSubset. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = IsSubset(a, b)
# logical operations
def toNOT(node):
	''' Convert expression of ! operation to Booleano Not. '''
	x = node[0].value
	node.value = Not(x)
def toAND(node):
	''' Convert expression of & operation to Booleano And. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = And(a, b)
def toOR(node):
	''' Convert expression of | operation to Booleano Or. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = Or(a, b)
def toXOR(node):
	''' Convert expression of ^ operation to Booleano Xor. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = Xor(a, b)

###   <definition>
# recursive pattern(s)
group = Recursive()
operand = Recursive()
### tokens
	# StandardConfig tokens
		### Note: changed MEMBER and SUBSET as of now (unicode issue).
		# Logical connectives
NOT = Word('~', format='"~"')(drop)
AND = Word('&', format='"&"')(drop)
OR = Word('|', format='"|"')(drop)
XOR = Word('^', format='"^"')(drop)
		# Relational operators
EQ = Word('==', format='"=="')(drop)
NE = Word('!=', format='"!="')(drop)
LT = Word('<', format='"<"')(drop)
GT = Word('>', format='">"')(drop)
LE = Word('<=', format='"<="')(drop)
GE = Word('>=', format='">="')(drop)
		# Set operators
MEMBER = Word('MEMBER', format='"MEMBER"')(drop)
SUBSET = Word('SUBSET', format='"SUBSET"')(drop)
SET_START = Word('{', format='"{"')(drop)
SET_END = Word('}', format='"}"')(drop)
ELEMENT_SEPARATOR = Word(',', format='","')(drop)
		# Grouping marks
GROUP_START = Word('(', format='"("')(drop)
GROUP_END = Word(')', format='")"')(drop)
		### Do not drop string delimiters to allow doubling.
STRING_START = Word('"', format='"\\""')
STRING_END = Word('"', format='"\\""')
		# Token internal characters
DECIMAL_SEPARATOR = Char('.', format="'.'")(drop)
		### Do not drop integer sep & ID spacing !
INTEGER_SEPARATOR = Char(',', format="','")
ID_SPACING = Char('_', format="'_'")
		# minus sign
MINUS = Word('-', format='"-"')
	# spacing & separation
SPACING = String(Klass(format='[\\t ]', charset='\t '), numMin=1,numMax=False, format='[\\t ]+')(drop)
OPT_SPC = String(Klass(format='[\\t ]', charset='\t '), numMin=False,numMax=False, format='[\\t ]*')(drop)
SET_SEP = Sequence([OPT_SPC, ELEMENT_SEPARATOR, OPT_SPC], format='OPT_SPC ELEMENT_SEPARATOR OPT_SPC')(drop)
	# operators with spacing -- derived from standard config
MINUS_ = Sequence([Word('-', format='"-"'), OPT_SPC], format='"-" OPT_SPC')
		# Logical connectives
NOT_ = Sequence([NOT, OPT_SPC], format='NOT OPT_SPC')(drop)
_AND_ = Sequence([OPT_SPC, AND, OPT_SPC], format='OPT_SPC AND OPT_SPC')(drop)
_OR_ = Sequence([OPT_SPC, OR, OPT_SPC], format='OPT_SPC OR OPT_SPC')(drop)
_XOR_ = Sequence([OPT_SPC, XOR, OPT_SPC], format='OPT_SPC XOR OPT_SPC')(drop)
		# Relational operators
_EQ_ = Sequence([OPT_SPC, EQ, OPT_SPC], format='OPT_SPC EQ OPT_SPC')(drop)
_NE_ = Sequence([OPT_SPC, NE, OPT_SPC], format='OPT_SPC NE OPT_SPC')(drop)
_LT_ = Sequence([OPT_SPC, LT, OPT_SPC], format='OPT_SPC LT OPT_SPC')(drop)
_GT_ = Sequence([OPT_SPC, GT, OPT_SPC], format='OPT_SPC GT OPT_SPC')(drop)
_LE_ = Sequence([OPT_SPC, LE, OPT_SPC], format='OPT_SPC LE OPT_SPC')(drop)
_GE_ = Sequence([OPT_SPC, GE, OPT_SPC], format='OPT_SPC GE OPT_SPC')(drop)
_MEMBER_ = Sequence([OPT_SPC, Word('MEMBER', format='"MEMBER"'), OPT_SPC], format='OPT_SPC "MEMBER" OPT_SPC')(drop)
_SUBSET_ = Sequence([OPT_SPC, Word('SUBSET', format='"SUBSET"'), OPT_SPC], format='OPT_SPC "SUBSET" OPT_SPC')(drop)
	# character classes
DIGIT = Klass(format='[0..9]', charset='0123456789')
ID_SPECIFIC_CHAR = Choice([Klass(format='[a..z  A..Z]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'), ID_SPACING], format='[a..z  A..Z] / ID_SPACING')
ID_SUITE_CHAR = Choice([Klass(format='[a..z  A..Z  0..9]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), ID_SPACING], format='[a..z  A..Z  0..9] / ID_SPACING')
		# Double (end) string delimiter to escape it.
		# Other characters are all safe
DBL_STRING_END = Sequence([STRING_END, STRING_END], format='STRING_END STRING_END')(simpleStringEnd)
		# String character class limited to inline ASCII for test.
SAFE_STRING_CHAR = Sequence([NextNot(STRING_END, format='!STRING_END'), Klass(format='[ \\t  \\x21..\\x7e]', charset=' \t!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~')], format='!STRING_END [ \\t  \\x21..\\x7e]')
STRING_CHAR = Choice([DBL_STRING_END, SAFE_STRING_CHAR], format='DBL_STRING_END / SAFE_STRING_CHAR')
# operands
	# These are base operands for operations that yield truth values:
	# namely comparisons and set operations.
	# Logical operations instead take *and* return truth values.
	### @@@ operand is recursive because of sets @@@
	# number
		#   INTEGER_GROUPING_NUMBER is checked in validation.
digits = Repetition(DIGIT, numMin=1,numMax=False, format='DIGIT+')(join)
integral_part = Repetition(Choice([DIGIT, INTEGER_SEPARATOR], format='DIGIT / INTEGER_SEPARATOR'), numMin=1,numMax=False, format='(DIGIT / INTEGER_SEPARATOR)+')(join, validateInt)
fractional_part = Sequence([DECIMAL_SEPARATOR, digits], format='DECIMAL_SEPARATOR digits')(join)
integer = Sequence([Option(MINUS_, format='MINUS_?'), integral_part], format='MINUS_? integral_part')(join)
real = Sequence([integer, fractional_part], format='integer fractional_part')(writeReal)
number = Choice([real, integer], format='real / integer')(toNumber)
	# string
stringChars = Repetition(STRING_CHAR, numMin=False,numMax=False, format='STRING_CHAR*')(join)
string = Sequence([STRING_START, stringChars, STRING_END], format='STRING_START stringChars STRING_END')(toString)
	# set
		### Note: Set must be frozen to allow nesting!
elements = Sequence([operand, Repetition(Sequence([SET_SEP, operand], format='SET_SEP operand'), numMin=False,numMax=False, format='(SET_SEP operand)*')], format='operand (SET_SEP operand)*')(intoList)
set_ = Sequence([SET_START, elements, SET_END], format='SET_START elements SET_END')(liftValue, toSet)
	# ID
		### Note: as of now did not follow the rule that
		#   ID names may start with digit.
ID = Sequence([Repetition(DIGIT, numMin=False,numMax=False, format='DIGIT*'), ID_SPECIFIC_CHAR, Repetition(ID_SUITE_CHAR, numMin=False,numMax=False, format='ID_SUITE_CHAR*')], format='DIGIT* ID_SPECIFIC_CHAR ID_SUITE_CHAR*')(join, getVar)
	# any kind of operand
		### @@@ pattern operand is recursive into set_ element @@@
		### Note: Shouldn't operand allow group?
		### Note: number must be matched after ID to avoid confusion
		#		 with IDs starting with one or more digit(s)
operand **= Choice([set_, string, ID, number], format='set_ / string / ID / number')
# operations
	# comparison: takes base operands, yield logic value
eqComp = Sequence([operand, _EQ_, operand], format='operand _EQ_ operand')(toEQ)
neComp = Sequence([operand, _NE_, operand], format='operand _NE_ operand')(toNE)
gtComp = Sequence([operand, _GT_, operand], format='operand _GT_ operand')(toGT)
ltComp = Sequence([operand, _LT_, operand], format='operand _LT_ operand')(toLT)
geComp = Sequence([operand, _GE_, operand], format='operand _GE_ operand')(toGE)
leComp = Sequence([operand, _LE_, operand], format='operand _LE_ operand')(toLE)
comparison = Choice([eqComp, neComp, ltComp, gtComp, leComp, geComp], format='eqComp / neComp / ltComp / gtComp / leComp / geComp')
	# set operation: takes specific operands, yields logic value
memberOperation = Sequence([operand, _MEMBER_, set_], format='operand _MEMBER_ set_')(toMEMBER)
subsetOperation = Sequence([set_, _SUBSET_, set_], format='set_ _SUBSET_ set_')(toSUBSET)
setOperation = Choice([memberOperation, subsetOperation], format='memberOperation / subsetOperation')
	# logic operation: takes logic operand(s), yields logic value
notOperand = Choice([group, setOperation, comparison], format='group / setOperation / comparison')
notOperation = Sequence([NOT_, notOperand], format='NOT_ notOperand')(toNOT)
andOperand = Choice([notOperation, notOperand], format='notOperation / notOperand')
andOperation = Sequence([andOperand, _AND_, andOperand], format='andOperand _AND_ andOperand')(toAND)
orOperand = Choice([andOperation, andOperand], format='andOperation / andOperand')
orOperation = Sequence([orOperand, _OR_, orOperand], format='orOperand _OR_ orOperand')(toOR)
xorOperation = Sequence([orOperand, _XOR_, orOperand], format='orOperand _XOR_ orOperand')(toXOR)
logicOperation = Choice([xorOperation, orOperation, andOperation, notOperation], format='xorOperation / orOperation / andOperation / notOperation')
	# group from operation (all return logical value)
operation = Choice([logicOperation, setOperation, comparison], format='logicOperation / setOperation / comparison')
group **= Sequence([GROUP_START, operation, GROUP_END], format='GROUP_START operation GROUP_END')(liftNode)
		### anyOperand just for test funcs:
anyOperand = Choice([operand, group], format='operand / group')
result = Choice([operation, operand, group], format='operation / operand / group')
# assignment -- just for fun
_ASSIGNMENT_ = Sequence([OPT_SPC, Word(':', format='":"'), OPT_SPC], format='OPT_SPC ":" OPT_SPC')(drop)
name = Sequence([ID_SPECIFIC_CHAR, Repetition(ID_SUITE_CHAR, numMin=False,numMax=False, format='ID_SUITE_CHAR*')], format='ID_SPECIFIC_CHAR ID_SUITE_CHAR*')(join)
value = Choice([operation, operand], format='operation / operand')
assignment = Sequence([name, _ASSIGNMENT_, result], format='name _ASSIGNMENT_ result')(setVar)



standardSoloParser._recordPatterns(vars())
standardSoloParser._setTopPattern("assignment")
standardSoloParser.grammarTitle = "standardSolo"
standardSoloParser.fileName = "standardSoloParser.py"
