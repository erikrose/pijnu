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
### import/export
import sys
end = sys.exit
from pijnu import writeParser

### standard config parameters-- just for memo
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
	T_ID_SPACING = "_"
	T_DECIMAL_SEPARATOR = "."
	T_INTEGER_SEPARATOR = ","
	INTEGER_GROUPING_NUMBER = 3
	MINUS = "-"
#
### get parser
def getParser():
	standard_grammar = file("standardSolo.pijnu").read()
	writeParser(standard_grammar)
	from standardSoloParser import standardSoloParser as parser
	return parser
#
#
### testing ######################################################
RULER = 33 * '*'
def testOperand():
	# operand	: group / set / string / number	: @
	# without IDs (vars & funcs)
	print "=== numbers (last ones are invalid) ==="
	source = """
	1
	54321
	4,321
	0,987,654,321
	-1234
	-1,234
	1,234,089.567
	,1 1, 1,1 9,87,654,321	# invalid ints
	"""
	parser.number.test(source,"findAll")
	print "=== other operands ==="
	source = """
	"foo bar"
	"foo""bar"
	{1,2.3}
	{1, 2.3}
	{-1,234.567,"foo bar",{1,2,3},{1, 2, 3}}
	(1<=2)
	(1 MEMBER {0, 1, 2})
	((1==2) | (1!=2))
	"""
	parser.anyOperand.test(source,"findAll")
	print "=== some failing operands"
	source = """
	1;1			# 2 ints
	1_1			# ditto
	{1,1}		# single int in set!!!
	(1)
	(1|)
	"""
	parser.anyOperand.test(source,"findAll")

def testID():
	print "=== ID ==="
	source = """
	a
	aaa
	_
	___
	_a_a_a_
	1_
	_1
	123rdFool
	(a==b)
	((a==b) | (a!=b))
	"""
	parser.anyOperand.test(source,"findAll")
	print "=== failing IDs"
	source = """
	a;b		# 2 IDs
	c,d		# ditto
	123		# integer
	(z)
	(a==b c==d)
	"""
	parser.anyOperand.test(source,"findAll")

def testComparison():
	print "=== comparison ==="
	source = """
	a==b
	a=="a"
	1=="1"
	1.0!="1"
	1==1.0
	1==1.1
	1!=1.1
	1!=1.0
	"az"=="az"
	"az"=="qw"
	{1, 2, 3}=={3, 2, 1}
	{1, 2, 3}!={3, 2, 0}
	{1, 2, {3, 2, 1}}=={2, {3, 2, 1}, 1}
	1<=1.1
	1>=1.1
	1>0.9
	1<0.9
	"""
	# result: T F T F   T F T F   T F   T T T   T F T F
	parser.comparison.test(source,"findAll")

def testSet():
	print "=== set & set operation ==="
	source = """
	{1, "foo"}
	{1, "foo", {1, 2, 3}}
	1 MEMBER {1, "foo"}
	"foo" MEMBER {1, "foo"}
	2 MEMBER {1, "foo"}
	"bar" MEMBER {1, "foo"}
	{"a", {"a"}} SUBSET {1, 2, 3}
	{1, 2} SUBSET {1, 2, 3}
	{1, "foo"} SUBSET {1, "foo", {1, 2, 3}}
	{2, "bar"} SUBSET {1, "foo", {1, 2, 3}}
	{1, {1, 2, 3}} SUBSET {1, "foo", {1, 2, 3}}
	"""
	# result: T T F F   T F T
 	parser.set_.test(source,"findAll")
 	parser.setOperation.test(source,"findAll")

def testLogic():
	print "=== logic ==="
	source = """
	~ 1 == 1.0
	~"a" != "b"
	~			1 MEMBER {1, 2, 3}
	~(~1==1)
	
	"az"=="az" & 1==1.0
	("az"=="az") & ("az"=="qw")
	{1, 2, 3}=={3, 2, 1} & {1, 2, {3, 2, 1}}=={2, {2, 1, 3}, 1}
	1==1 & (~1==1|1==1.01)
	
	(1<=1.1) | (1>=1.1)
	1>1.1 | 1<0.9
	~1 == 1 | "a" == "a" & 1 == 1.000
	(~1 == 1 | "a" == "a") | 1 == 1.000
	
	1>1.1 ^ 1<0.9
	1>1.1 & 1==1 ^ 1>0.9
	1>1.1 ^ (1>0.9 ^ ~1.000 != 1.0)
	"""
	# last op: (F ^ T) ^ ~F ==> T ^ T ==> F
	# result: F T F   T F T F   T F T   F T F
	parser.logicOperation.test(source,"findAll")

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
	testOperand()
	print RULER
	testID()
	print RULER
	testComparison()
	print RULER
	testSet()
	print RULER
	testLogic()
	print RULER
	testAssignment()
	pass

if __name__ == "__main__":
	parser = getParser()
	test()
