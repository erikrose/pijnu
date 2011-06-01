""" standardDirect
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
# StandardConfig tokens for testing only
	### Note: changed MEMBER and SUBSET as of know (unicode issue)
	### Note: changed ELEMENT_SEPARATOR to ';' (conflict with integer sep),
	#   but should rather be spacing and not configurable.
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
	ELEMENT_SEPARATOR	: ";"+					: drop
	# Grouping marks
	STRING_START 		: "\""					: drop
	STRING_END 			: "\""					: drop
	GROUP_START		 	: "("					: drop
	GROUP_END 			: ")"					: drop
	# Token internal characters
	DECIMAL_SEPARATOR	: '.'					: drop
	INTEGER_SEPARATOR	: ','					: drop
	### no drop var spacing !
	VARIABLE_SPACING 	: '_'					: 
# spacing & separation
	SPACING			: [\t ]+					: drop
	OPT_SPC			: [\t ]*					: drop
	SET_SEP			: OPT_SPC ELEMENT_SEPARATOR OPT_SPC	: drop
# constant tokens -- most (all?) are provided by config
	### MINUS sign !!!
	MINUS			: "-"
	# Logical connectives
	_NOT_			: OPT_SPC "~" OPT_SPC		: drop
	_AND_ 			: OPT_SPC "&" OPT_SPC		: drop
	_OR_ 			: OPT_SPC "|" OPT_SPC		: drop
	_XOR_ 			: OPT_SPC "^" OPT_SPC		: drop
	# Relational operators
	_EQ_			: OPT_SPC "==" OPT_SPC		: drop
	_NE_ 			: OPT_SPC "!=" OPT_SPC		: drop
	_LT_ 			: OPT_SPC "<" OPT_SPC		: drop
	_GT_ 			: OPT_SPC ">" OPT_SPC		: drop
	_LE_ 			: OPT_SPC "<=" OPT_SPC		: drop
	_GE_ 			: OPT_SPC ">=" OPT_SPC		: drop
	_MEMBER_		: OPT_SPC "MEMBER" OPT_SPC	: drop
	_SUBSET_ 		: OPT_SPC "SUBSET" OPT_SPC	: drop
# character classes
	VAR_START		: [a..z  A..Z] / VARIABLE_SPACING
	VAR_SUITE		: [a..z  A..Z  0..9] / VARIABLE_SPACING
	DIGIT			: [0..9]
	### precisely specifiy the list of unsafe chars in a string!!!
	### then add syntax for excepted chars (eg '""' for '"')
	# string char limited to ASCII for test (except '"')
	STRING_CHAR		: [ \t  \x21..\x7e  !!\"]

# base operands
	### Note: seems that var names belong to a fix set.
	#   as they should be translatable
	### Note: as of now did not follow the rule that
	#   var names may start with digit.
	var				: VAR_START VAR_SUITE*					: join getVar
	# integers and reals are both treated as floats
	### Note: seems that reals cannot end with decimal point.
	### Note: I let user flexibility for the place of INTEGER_SEPARATOR
	#   'cause there are variants (renamed from THOUSANDS_SEPARATOR)
	### Note: number comparison should throw custom exception when fails.
	### Note: what about sign?
	### Note: operand is recursive because of sets
	digits			: DIGIT+								: join
	integral_part	: digits (INTEGER_SEPARATOR digits)*	: intoList join
	fractional_part	: DECIMAL_SEPARATOR digits				: join
	integer			: MINUS? integral_part					: join
	real			: integer fractional_part				: writeReal
	number			: real / integer						: toReal
	### Note: string constant comparisons seem unclear.
	stringChars		: STRING_CHAR*
	string			: STRING_START stringChars STRING_END	: join
	# set
	### Note: Set must be frozen to allow nesting!
	elements		: operand (SET_SEP operand)*			: intoList
	set_			: SET_START elements SET_END			: liftValue toSet
	# operand
	### @@@ pattern operand is recursive into set_ element @@@
	### Note: Shouldn't operand allow group?
	operand			: set_ / string / number / var			: @

# operations
	### TODO: write transforms to yield booleano Operator objects.
	# comparison: takes base operands, yield logic
	eqOperation		: operand _EQ_ operand					: doEQ
	neOperation		: operand _NE_ operand					: doNE
	gtOperation		: operand _GT_ operand					: doGT
	ltOperation		: operand _LT_ operand					: doLT
	geOperation		: operand _GE_ operand					: doGE
	leOperation		: operand _LE_ operand					: doLE
	comparison		: eqOperation / neOperation / ltOperation / gtOperation / leOperation / geOperation
	# set operation: takes specific operands, yields logic
	memberOperation	: (var/operand) _MEMBER_ (var/set_)		: doMEMBER
	subsetOperation	: (var/set_) _SUBSET_ (var/set_)		: doSUBSET
	setOperation	: memberOperation / subsetOperation
	# logic operation: takes logic operands, yields logic
	notOperation	: NOT (var / group)				: doNOT
	logic_operand	: notOperation / var / group
	andOperation	: logic_operand _AND_ logic_operand		: doOR
	orOperation		: logic_operand _OR_ logic_operand		: doAND
	xorOperation	: logic_operand _XOR_ logic_operand		: doXOR
	logicOperation	: xorOperation / orOperation / andOperation / notOperation
	# group from operation
	operation		: logicOperation / setOperation / comparison
	group			: GROUP_START operation GROUP_END		: @ liftNode
		### just for test:
	anyOperand		: operand / group
	result			: operation / operand / group
# assignment -- just for fun
	_ASSIGNMENT_	: OPT_SPC ":" OPT_SPC					: drop
	name			: VAR_START VAR_SUITE*					: join
	value			: operation / operand
	assignment		: name _ASSIGNMENT_ result				: setVar

"""



from pijnu.library import *

standardDirectParser = Parser()
state = standardDirectParser.state



### title: standardDirect ###
###   <toolset>
def writeReal(node):
	''' Write expression of real number
		from integral and fractional parts. '''
	(int_part,fract_part) = (node[0].value,node[1].value)
	node.value = "%s.%s" %(int_part,fract_part) 
def toSet(node):
	''' Convert set_ node value to python (frozen) set. '''
	elements = [child.value for child in node]
	node.value = Set(elements)
def doEQ(node):
	''' Perform == operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a == b)
def doNE(node):
	''' Perform != operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a != b)
def doGT(node):
	''' Perform > operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a > b)
def doLT(node):
	''' Perform < operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a < b)
def doGE(node):
	''' Perform >= operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a >= b)
def doLE(node):
	''' Perform <= operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a <= b)
def doNOT(node):
	''' Perform ! operation. '''
	x = node[0].value
	node.value = (not x)
def doAND(node):
	''' Perform | operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a | b)
def doOR(node):
	''' Perform & operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a & b)
def doXOR(node):
	''' Perform ^ operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a ^ b)
def doMEMBER(node):
	''' Perform MEMBER operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a in b)
def doSUBSET(node):
	''' Perform SUBSET operation. '''
	(a,b) = (node[0].value,node[1].value)
	node.value = (a.issubset(b))
def getVar(node):
	''' (Try to) get var value from state. '''
	name = node.value
	try:
		value = getattr(state, name)
		node.value = value
		print "%s --> %s" %(name, value)
	except AttributeError:
		# for testing
		node.value = 0
def setVar(node):
	''' Bind var name & value as state attribute. '''
	(name,value) = (node[0].value,node[1].value)
	setattr(state, name, value)
	print "%s <-- %s" %(name, value)

###   <definition>
# recursive pattern(s)
group = Recursive()
operand = Recursive()
# StandardConfig tokens for testing only
	### Note: changed MEMBER and SUBSET as of know (unicode issue)
	### Note: changed ELEMENT_SEPARATOR to ';' (conflict with integer sep),
	#   but should rather be spacing and not configurable.
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
ELEMENT_SEPARATOR = Repetition(Word(';', format='";"'), numMin=1,numMax=False, format='";"+')(drop)
	# Grouping marks
STRING_START = Word('"', format='"\\""')(drop)
STRING_END = Word('"', format='"\\""')(drop)
GROUP_START = Word('(', format='"("')(drop)
GROUP_END = Word(')', format='")"')(drop)
	# Token internal characters
DECIMAL_SEPARATOR = Char('.', format="'.'")(drop)
INTEGER_SEPARATOR = Char(',', format="','")(drop)
	### no drop var spacing !
VARIABLE_SPACING = Char('_', format="'_'")
# spacing & separation
SPACING = String(Klass(format='[\\t ]', charset='\t '), numMin=1,numMax=False, format='[\\t ]+')(drop)
OPT_SPC = String(Klass(format='[\\t ]', charset='\t '), numMin=False,numMax=False, format='[\\t ]*')(drop)
SET_SEP = Sequence([OPT_SPC, ELEMENT_SEPARATOR, OPT_SPC], format='OPT_SPC ELEMENT_SEPARATOR OPT_SPC')(drop)
# constant tokens -- most (all?) are provided by config
	### MINUS sign !!!
MINUS = Word('-', format='"-"')
	# Logical connectives
_NOT_ = Sequence([OPT_SPC, Word('~', format='"~"'), OPT_SPC], format='OPT_SPC "~" OPT_SPC')(drop)
_AND_ = Sequence([OPT_SPC, Word('&', format='"&"'), OPT_SPC], format='OPT_SPC "&" OPT_SPC')(drop)
_OR_ = Sequence([OPT_SPC, Word('|', format='"|"'), OPT_SPC], format='OPT_SPC "|" OPT_SPC')(drop)
_XOR_ = Sequence([OPT_SPC, Word('^', format='"^"'), OPT_SPC], format='OPT_SPC "^" OPT_SPC')(drop)
	# Relational operators
_EQ_ = Sequence([OPT_SPC, Word('==', format='"=="'), OPT_SPC], format='OPT_SPC "==" OPT_SPC')(drop)
_NE_ = Sequence([OPT_SPC, Word('!=', format='"!="'), OPT_SPC], format='OPT_SPC "!=" OPT_SPC')(drop)
_LT_ = Sequence([OPT_SPC, Word('<', format='"<"'), OPT_SPC], format='OPT_SPC "<" OPT_SPC')(drop)
_GT_ = Sequence([OPT_SPC, Word('>', format='">"'), OPT_SPC], format='OPT_SPC ">" OPT_SPC')(drop)
_LE_ = Sequence([OPT_SPC, Word('<=', format='"<="'), OPT_SPC], format='OPT_SPC "<=" OPT_SPC')(drop)
_GE_ = Sequence([OPT_SPC, Word('>=', format='">="'), OPT_SPC], format='OPT_SPC ">=" OPT_SPC')(drop)
_MEMBER_ = Sequence([OPT_SPC, Word('MEMBER', format='"MEMBER"'), OPT_SPC], format='OPT_SPC "MEMBER" OPT_SPC')(drop)
_SUBSET_ = Sequence([OPT_SPC, Word('SUBSET', format='"SUBSET"'), OPT_SPC], format='OPT_SPC "SUBSET" OPT_SPC')(drop)
# character classes
VAR_START = Choice([Klass(format='[a..z  A..Z]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'), VARIABLE_SPACING], format='[a..z  A..Z] / VARIABLE_SPACING')
VAR_SUITE = Choice([Klass(format='[a..z  A..Z  0..9]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'), VARIABLE_SPACING], format='[a..z  A..Z  0..9] / VARIABLE_SPACING')
DIGIT = Klass(format='[0..9]', charset='0123456789')
	### precisely specifiy the list of unsafe chars in a string!!!
	### then add syntax for excepted chars (eg '""' for '"')
	# string char limited to ASCII for test (except '"')
STRING_CHAR = Klass(format='[ \\t  \\x21..\\x7e  !!\\"]', charset=" \t!#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~")
# base operands
	### Note: seems that var names belong to a fix set.
	#   as they should be translatable
	### Note: as of now did not follow the rule that
	#   var names may start with digit.
var = Sequence([VAR_START, Repetition(VAR_SUITE, numMin=False,numMax=False, format='VAR_SUITE*')], format='VAR_START VAR_SUITE*')(join, getVar)
	# integers and reals are both treated as floats
	### Note: seems that reals cannot end with decimal point.
	### Note: I let user flexibility for the place of INTEGER_SEPARATOR
	#   'cause there are variants (renamed from THOUSANDS_SEPARATOR)
	### Note: number comparison should throw custom exception when fails.
	### Note: what about sign?
	### Note: operand is recursive because of sets
digits = Repetition(DIGIT, numMin=1,numMax=False, format='DIGIT+')(join)
integral_part = Sequence([digits, Repetition(Sequence([INTEGER_SEPARATOR, digits], format='INTEGER_SEPARATOR digits'), numMin=False,numMax=False, format='(INTEGER_SEPARATOR digits)*')], format='digits (INTEGER_SEPARATOR digits)*')(intoList, join)
fractional_part = Sequence([DECIMAL_SEPARATOR, digits], format='DECIMAL_SEPARATOR digits')(join)
integer = Sequence([Option(MINUS, format='MINUS?'), integral_part], format='MINUS? integral_part')(join)
real = Sequence([integer, fractional_part], format='integer fractional_part')(writeReal)
number = Choice([real, integer], format='real / integer')(toReal)
	### Note: string constant comparisons seem unclear.
stringChars = Repetition(STRING_CHAR, numMin=False,numMax=False, format='STRING_CHAR*')
string = Sequence([STRING_START, stringChars, STRING_END], format='STRING_START stringChars STRING_END')(join)
	# set
	### Note: Set must be frozen to allow nesting!
elements = Sequence([operand, Repetition(Sequence([SET_SEP, operand], format='SET_SEP operand'), numMin=False,numMax=False, format='(SET_SEP operand)*')], format='operand (SET_SEP operand)*')(intoList)
set_ = Sequence([SET_START, elements, SET_END], format='SET_START elements SET_END')(liftValue, toSet)
	# operand
	### @@@ pattern operand is recursive into set_ element @@@
	### Note: Shouldn't operand allow group?
operand **= Choice([set_, string, number, var], format='set_ / string / number / var')
# operations
	### TODO: write transforms to yield booleano Operator objects.
	# comparison: takes base operands, yield logic
eqOperation = Sequence([operand, _EQ_, operand], format='operand _EQ_ operand')(doEQ)
neOperation = Sequence([operand, _NE_, operand], format='operand _NE_ operand')(doNE)
gtOperation = Sequence([operand, _GT_, operand], format='operand _GT_ operand')(doGT)
ltOperation = Sequence([operand, _LT_, operand], format='operand _LT_ operand')(doLT)
geOperation = Sequence([operand, _GE_, operand], format='operand _GE_ operand')(doGE)
leOperation = Sequence([operand, _LE_, operand], format='operand _LE_ operand')(doLE)
comparison = Choice([eqOperation, neOperation, ltOperation, gtOperation, leOperation, geOperation], format='eqOperation / neOperation / ltOperation / gtOperation / leOperation / geOperation')
	# set operation: takes specific operands, yields logic
memberOperation = Sequence([Choice([var, operand], format='var/operand'), _MEMBER_, Choice([var, set_], format='var/set_')], format='(var/operand) _MEMBER_ (var/set_)')(doMEMBER)
subsetOperation = Sequence([Choice([var, set_], format='var/set_'), _SUBSET_, Choice([var, set_], format='var/set_')], format='(var/set_) _SUBSET_ (var/set_)')(doSUBSET)
setOperation = Choice([memberOperation, subsetOperation], format='memberOperation / subsetOperation')
	# logic operation: takes logic operands, yields logic
notOperation = Sequence([NOT, Choice([var, group], format='var / group')], format='NOT (var / group)')(doNOT)
logic_operand = Choice([notOperation, var, group], format='notOperation / var / group')
andOperation = Sequence([logic_operand, _AND_, logic_operand], format='logic_operand _AND_ logic_operand')(doOR)
orOperation = Sequence([logic_operand, _OR_, logic_operand], format='logic_operand _OR_ logic_operand')(doAND)
xorOperation = Sequence([logic_operand, _XOR_, logic_operand], format='logic_operand _XOR_ logic_operand')(doXOR)
logicOperation = Choice([xorOperation, orOperation, andOperation, notOperation], format='xorOperation / orOperation / andOperation / notOperation')
	# group from operation
operation = Choice([logicOperation, setOperation, comparison], format='logicOperation / setOperation / comparison')
group **= Sequence([GROUP_START, operation, GROUP_END], format='GROUP_START operation GROUP_END')(liftNode)
		### just for test:
anyOperand = Choice([operand, group], format='operand / group')
result = Choice([operation, operand, group], format='operation / operand / group')
# assignment -- just for fun
_ASSIGNMENT_ = Sequence([OPT_SPC, Word(':', format='":"'), OPT_SPC], format='OPT_SPC ":" OPT_SPC')(drop)
name = Sequence([VAR_START, Repetition(VAR_SUITE, numMin=False,numMax=False, format='VAR_SUITE*')], format='VAR_START VAR_SUITE*')(join)
value = Choice([operation, operand], format='operation / operand')
assignment = Sequence([name, _ASSIGNMENT_, result], format='name _ASSIGNMENT_ result')(setVar)



standardDirectParser._recordPatterns(vars())
standardDirectParser._setTopPattern("assignment")
standardDirectParser.grammarTitle = "standardDirect"
standardDirectParser.fileName = "standardDirectParser.py"
