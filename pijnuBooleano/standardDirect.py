# coding: utf-8


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
from pijnu import writeParser
from sys import exit as end
Set = frozenset

class UNDEF(object):
	''' unique sentinel 
		--> for yet undefined var data
		'''
	pass

class Variable(object):
	''' booleano var
		~ Holds name and possibly data.
		'''
	def __init__(self, name, data=UNDEF()):
		self.name = name
		self.data = data
	def __getattr__(self, attr_name):
		try:
			return getattr(self.data, attr_name)
		except AttributeError, e:
			if isinstance(self.data, UNDEF):
				message = "Variable '%s' has no value" % self.name
				raise ValueError(message)
			else:
				raise e

class StandardConfig(object):
	''' set of default tokens & operators
		(should be a module later)
		~ All are strings as of now:
			--> Either change them to pattern definitions.
			--> Or let a transformation do the job.
		In both cases, some of them may also need transforms
		-- actually most will need at least 'drop'.
		'''
	# Some logical connectives:
	T_NOT = "~"
	T_AND = "&"
	T_OR = "|"
	T_XOR = "^"
	# Relational operators:
	T_EQ = "=="
	T_NE = "!="
	T_LT = "<"
	T_GT = ">"
	T_LE = "<="
	T_GE = ">="
	# Set operators:
	T_IN = u"∈"
	T_CONTAINED = u"⊂"
	T_SET_START = "{"
	T_SET_END = "}"
	T_ELEMENT_SEPARATOR = ","
	# Grouping marks:
	T_STRING_START = '"'
	T_STRING_END = '"'
	T_GROUP_START = "("
	T_GROUP_END = ")"
	# Miscellaneous tokens:
	T_VARIABLE_SPACING = "_"
	T_DECIMAL_SEPARATOR = "."
	T_THOUSANDS_SEPARATOR = ","


standard_grammar = r"""
standardDirect
<toolset>
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
<definition>
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
#
#
### get parser
def getParser():
	writeParser(standard_grammar)
	from standardDirectParser import standardDirectParser as parser
	return parser
#
#
### testing ######################################################
RULER = 33 * '*'
def testOperand():
	#operand	: group / set / string / number / var	: @
	print "=== operand ==="
	source = """
	a
	ab_zyx_
	-1,234
	1,234,089.567
	"foo bar"
	{1;2}
	{a;az;	-1,234	  ;	1,234.567;"foo bar";{1;2;3}}
	(a<=b)
	(a!=b)
	(~a)
	(a & b)
	(a | b)
	(a ^ (~b))
	(a|(b^(~c)))
	"""
	parser.anyOperand.test(source,"findAll")
	print "=== failing operands"
	source = """
	1;1			# 2 ints
	1_1			# ditto
	a;a			# 2 vars
	{1,1}		# 1 single int in set!!!
	(a)
	(a|)
	"""
	parser.anyOperand.test(source,"findAll")

def testComparison():
	print "=== comparison ==="
	source = """
	1==1.0
	a==b
	a=="a"
	1!=1.1
	"az"=="az"
	"az"=="qw"
	{1;2;3}=={3;2;1}
	{1;2;3}!={3;2;0}
	{1;2;{3;2;1}}=={2;{3;2;1};1}
	1<=1.1
	1>=1.1
	1>0.9
	1<0.9
	"""
	parser.comparison.test(source,"findAll")
	# result: T T F T   T F   T T T   T F T F

def testLogic():
	print "=== logic ==="
	source = """
	~(1 == 1.0)
	~("a" == "b")
	~(1!=1.1)
	("az"=="az") & ("az"=="qw")
	("az"=="az") & (1==1.0)
	({1;2;3}=={3;2;1}) & ({1;2;{3;2;1}}=={2;{3;2;1};1})
	(1==1) & ((~(1==1)) | (1==1.01))
	(1<=1.1) | (1>=1.1)
	(1>1.1) | (1<0.9)
	~(1 == 1) | (("a" == "a") & (1 == 1.000))
	(1>1.1) ^ (1<0.9)
	(1>1.1) ^ (1>0.9)
	((1>1.1) ^ (1>0.9)) ^ ~(1.000 != 1.0)
	"""
	# last op: (F ^ T) ^ ~F ==> T ^ T ==> F
	# result: F T F   F T T F   T F T   F T F
	parser.logicOperation.test(source,"findAll")
	
def testSet():
	print "=== set operation ==="
	source = """
	{1;"foo"}
	{1;"foo";{1;2;3}}
	1 MEMBER {1;"foo"}
	"foo" MEMBER {1;"foo"}
	2 MEMBER {1;"foo"}
	"bar" MEMBER {1;"foo"}
	{1;"foo"} SUBSET {1;"foo";{1;2;3}}
	{2;"bar"} SUBSET {1;"foo";{1;2;3}}
	{1;{1;2;3}} SUBSET {1;"foo";{1;2;3}}
	"""
 	parser.set_.test(source,"findAll")
 	parser.setOperation.test(source,"findAll")
	# result: T T F F   T F T

def testAssignment():
	print "=== assignment ==="
	source = """
	a: 1
	b: "foo"
	c: {1;"foo"}
	d: {1;"foo";{1;2;3}}
	z: a
	y: (a == 1.0)
	x: (a MEMBER c)
	w: (c SUBSET d)
	"""
 	parser.assignment.test(source,"findAll")

def test():
	pass
#~ 	testOperand()
#~ 	print RULER
#~ 	testComparison()
#~ 	print RULER
#~ 	testLogic()
#~ 	print RULER
#~ 	testSet()
#~ 	print RULER
	testAssignment()

if __name__ == "__main__":
	parser = getParser()
	test()
