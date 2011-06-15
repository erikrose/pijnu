# coding: utf8


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
'''		p a r s e r
	
	a container for a set of patterns
	
	provides
		~ some structure/distinction
		~ overall config
		~ preprocessing
		~ collectPatterns: when used directly in code
		  -- will also name the patterns!
		~ resetMemo: for reusing patterns while testing
		~ state
	'''

### import/export
from pijnu.tools import *
# need to test for types Pattern & Recursive
from pattern import Pattern, Recursive, Char
from error import PijnuError
#from types import FunctionType as Function

class State(object):
	''' a container for state data
		~ Used to tansform parser into a kind of state machine
		  able to cope with contextual match validation.
		~ Data should be set on the state object as attributes.
		'''
#


### TODO :	remove pattern naming from collectPatterns,
###			when pijnuParser itself holds names
###			maybe add a namePatterns method instead
###			for hand-coded parsers.

class Parser(object):
	''' parser object
		* Result of:
			~ automatic parser generation
			~ manual generation from code
		* Is built from a collection of patterns.
		* Only a parser with defined top pattern
		  can be directly invoked for matching.
		'''
	''' example from code
		# create
		p1 = ...
		p2 = ...
		p3 = ...
		parser = Parser("name", locals())
		# match
		source = "..........."
		result = parser.match(source)
		snippet2 = "..."
		r2 = parser.p2.match(snippet)
		'''
	### creation
	def __init__(self, scope=None,
				topPatternName=None,
				grammarTitle=None,
				filename=None):
		''' Define patterns, top pattern, title.
			~ scope should be caller's vars(), or locals().
			~ For hand-coded grammar, only scope is necessary
			  either at init or when ready to collect patterns.
			~ From text grammar, top pattern and title are automatic.
			~ filename is here only to allow several variants of a parser
			  -- but it's better practice to differenciate grammar names.
			 '''
		# Record patterns as attributes automatically
		# if caller scope is passed at init.
		# (! beware name conflicts !)
		if scope is not None:
			self._recordPatterns(scope)
		# When a "top pattern" is defined, the parser can be invoked
		# for matching: it will delegate to its top pattern.
		# Otherwise a specific pattern must be used for matching.
		if scope is not None and topPatternName is not None:
			self._setTopPattern(topPatternName)
		# additional info
		self.filename = filename
		self.grammarTitle = grammarTitle
		# state -- for contextual operations
		self.state = State()
	def _setTopPattern(self, topPatternName):
		try:
			self.topPattern = getattr(self, topPatternName)
			self.canMatch = True
		except (AttributeError,TypeError):
			message = "Cannot find top pattern called '%s'." % topPatternName
			raise PijnuError(message)
	def _recordPatterns(self, scope):
		''' collect -- and name! -- patterns in scope
			~ patterns become attributes!
			~ scope should be vars() of caller scope '''
		for (name,obj) in scope.items():
			if isinstance(obj,Pattern):
				obj.parser = self
				setattr(self, name, obj)
				obj.name = name
				# case recursive pattern, name wrapped pattern as well
#~ 				if isinstance(obj,Recursive):
#~ 					obj.pattern.name = '@'+obj.name
	### parser match & test methods
	# --> delegate to top pattern
	# ~ A top pattern must have been defined...
	# ~ ...or pattern methods can be directly invoked.
	def match(self, source):
		''' Match start of source text.
			Return result tree/node or raise Failure error. '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.match(source)
	def matchTest(self, source):
		''' Match in test mode. '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.matchTest(source)
	def parse(self, source):
		''' Match whole of source text.
			Return result tree/node or raise Failure error. '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.parse(source)
	def parseTest(self, source):
		''' Parse in test mode. '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.parseTest(source)
	def findAll(self, source):
		''' Find & return all matches for pattern in source.
			~ Case none is found, result is empty sequence.
			~ Overlapping matches are not handled.
			~ findAll does *not* collect nil nodes! '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.findAll(source)
	def replace(self, source, value):
		''' Find all matches for pattern in source
			& replace them with given value.
			~ uses findAll '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.replace(source, value)
	def test(self, source, method_name="matchTest"):
		''' Try performing test match on source text;
			output result and return parse tree/node.
			Note that unlike testSuite, the default method is match. '''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.test(source, method_name)
	def testSuite(self, test_dict, method_name="parse", silent=False):
		''' Perform a test suite by asserting equality
			of expected and actual parse results.
			This method is rather intended to check that modifications
			did not create bugs, after a program has once run fine.
			~  test_dict holds {source:result} pairs
			~ result is in fact the string repr of a node *value*
			~ None result means expected failure.
			Use testSuiteDict to first get a test_dict.
			Note that unlike test, the default method is parse.
			'''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.testSuite(test_dict, method_name, silent)
	def testSuiteDict(self, sources, method_name="parse"):
		''' Return & print a test dict for testSuite.
			Note that this should be done only once!
			Can also be used alone just to run and output
			test matches on a sequence of source expressions.
			'''
		if not self.canMatch:
			message = "This parser cannot match directly (yet).\n" \
						"Either first define a top pattern\n" \
						"or invoke one of its pattern attributes."
			raise AttributeError(message)
		return self.topPattern.testSuiteDict(sources, method_name)
	### output
	def __str__(self):
		grammarInfo = "" if self.grammarTitle is None \
					else "'%s' " %self.grammarTitle
		fileInfo = "" if self.filename is None \
					else " -- from file '%s'" %self.filename
		return "<%sParser object%s>" % (grammarInfo, fileInfo)


#
### test #####################################
	
def testCode():
	print ("=== parser from code ===")
	w1 = Word("foo")
	w2 = Word("bar")
	ch = Choice([w1,w2])
	parser = Parser(vars(),"ch","test")
	print "parser		:", parser
	print "top pattern	:", parser.topPattern
	parser.test("foobaz")
def testGrammar():
	print ("=== parser from grammar ===")
	grammar = r"""
testParser
<definition>
	w1 : "foo"
	w2 : "bar"
	ch : w1 / w2
"""
	parser = makeParser(grammar)
	print "parser		:", parser
	print "top pattern	:", parser.topPattern
	parser.test("barfoz")
def testRecursion():
	print ("=== parser with recursion ===")
	# r : '(' r ')' / 'a'  -- r: (parenY / l)
	l 		= Char('a')
	(lparen,rparen)	= (Char('('),Char(')'))
	r 		= Recursive()
	parenY	= Sequence([lparen , r, rparen])
	r 		**= Choice([parenY, l])
	# parser
	parser = Parser(vars(),"r","test")
	print "parser		:", parser
	print "top pattern	:", parser.topPattern
	parser.test("(((a)))")
	
def test():
	testCode()
	testGrammar()
	testRecursion()
if __name__ == "__main__":
	# import for testing only
	from pijnu.library.pattern import *
	from pijnu.generator import makeParser
	test()
