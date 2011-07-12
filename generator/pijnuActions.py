# coding:utf8

'''		p i j n u   p a r s e r   m a t c h   a c t i o n s

	A set of match actions to change node values.
	Used by pijnu's meta parser to write user parser code.
'''


### import/export
# Note: export all names to pijnuParser
from pijnu.library.tools import *
from pijnu.library.node import Node, Nodes

### character format
CODE_MAP =  {
				'\\\\'	: '\\',
				'\\t'	: '\t',
				'\\n'	: '\n',
				'\\r'	: '\r',
				'\\\''	: '\'',
				'\\"'	: '"',
				'\\]'	: ']'
				}
def codeToChar(node):
	''' character from backslash coded character format '''
	# examples:
	# '\\\\' --> '\\'
	# '\\t'  --> '\t'
	# '\\]'  --> ']'
	node.value = CODE_MAP[node.value]
def hexToChar(node):
	''' Change hexadecimal ordinal format to character  '''
	# '\x61' --> 'a'
	ord = int(node[2:], 16)
	node.value = chr(ord)
def decToChar(node):
	''' Change decimal ordinal format to character  '''
	# '\097' --> 'a'
	ord = int(node[1:])
	node.value = chr(ord)


### item:  char, word, ranj, klass
def charCode(node):
	''' Change char node value to Char() expr. '''
	# example: 	'a'
	# --> 		char:'a'
	# --> 		Char('a')
	#
	# new node value
	# original format expr for pattern output
	expr = repr(node.snippet)
	# ~ use repr() to avoid trouble of control characters
	char = repr(node.value)
	node.value = "Char(%s, expression=%s)" % (char,expr)

def wordCode(node):
	''' Change word node value to Word() expr. '''
	# example: 	"xyz"
	# --> 		word:"xyz"
	# --> 		Word('xyz')
	#
	# original format expr for pattern output
	expr = repr(node.snippet)
	# ~ use repr() to avoid trouble of control characters
	word = repr(node.value)
	node.value = "Word(%s, expression=%s)" % (word,expr)

def ranjToCharset(node):
	''' Change ranj node value to expanded range charset. '''
	# example: 	"a..e"
	# --> 		ranj:"a..e"
	# --> 		ranj:"abcde"
	#
	# range borders (right-side included)
	(c1,c2) = (node[0].value,node[1].value)
	(n1,n2) = (ord(c1),ord(c2))
	# chars in range
	chars = [chr(n) for n in range(n1, n2+1)]
	# new node value
	node.value = ''.join(chars)

EXCLUSION = "!!"
def klassToCharset(node):
	''' Change klass node value to charset.
		~ Actually, there's only to remove possible excluded characters
		 (ranges have already been expanded) '''
	# example:	[a..e  0..9 *+  !!c0..6]
	# -->		klass:"abcde0123456789*+!!c0123456"		(rangeToCharset)
	# --> 		klass:'abde789+*'
	klass = node.value
	exclusion_count = klass.count(EXCLUSION)
	# case no EXCLUSION: nothing to do
	if exclusion_count == 0:
		pass
	# case 1 EXCLUSION: exclude right side from charset
	elif exclusion_count == 1:
		(included,excluded) = klass.split(EXCLUSION)
		chars = [c for c in included if c not in excluded]
		node.value = ''.join(chars)
	# case more than 1 EXCLUSION: error
	else:
		message = (	"Class expr cannot hold EXCLUSION code '!!'"
					" more than once.\n   %s" % klass)
		raise ValueError(message)

def klassCode(node):
	''' Change klass node value to Klass() expr. '''
	# example: 	[a..e  0..9  _ -  !!d0]
	# --> 		klass:"a..e  0..9  _ -  !!d0"
	# --> 		klass:"abcde0123456789_ -!!d0"	(rangeToCharset)
	# --> 		klass:"abce123456789_ -"		(klassToCharset)
	# --> 		Klass('abce123456789_ -', '[a..e  0..9  _ -  !!d0]')
	#
	# A class node can hold: range, "!!" EXCLUSION code, "  " KALSSSEP separator,
	# single character expr (litChat, codedChar, decChar, hexChar)
	#
	# original format for output, full charset for matching
	# (use repr() to avoid control character mess)
	expr = repr(node.snippet)
	charset = repr(node.value)
	# new node value
	# !!! format comes first here !!!
	node.value = "Klass(u%s, expression=%s)" % (charset, expr)

### term with affix: option, repetition, lookahead
def optionCode(node):
	''' Change option node value to option expr. '''
	# example: 	"foo"?
	# --> 		option:[Word("foo")]
	# --> 		Option(Word("foo"))
	#
	# new node value
	# original format expr for pattern output
	expr = repr(node.snippet)
	pattern = node.value[0].value
	node.value = "Option(%s, expression=%s)" % (pattern,expr)
def repetSuffixCode(node):
	''' Change repetition suffix node value to expression of repetition. '''
	# examples:
	# *			--> numMin=False,numMax=False
	# +			--> numMin=1,numMax=False
	# {3}		--> numMin=3,numMax=3
	# {3..9}	--> numMin=3,numMax=9
	# TODO:
	# {..9}		--> numMin=False,numMax=9
	# {3..}		--> numMin=3,numMax=False
	#
	# data
	repetTyp = node.tag
	# case sign: '*' or '+'
	if repetTyp == "ZEROORMORE":
		node.value = "numMin=False, numMax=False"
	elif repetTyp == "ONEORMORE":
		node.value = "numMin=1, numMax=False"
	# case numbering
	elif repetTyp == "number":
		n = node.value
		node.value = "numMin=%s, numMax=%s" % (n,n)
	elif repetTyp == "numRanj":
		(m,n) = (node[0].value,node[1].value)
		node.value = "numMin=%s, numMax=%s" % (m,n)
def repetitionCode(node):
	''' Change string node value to expr of repetition.
		* When the base pattern is a klass, or a simple char,
		  a String pattern will be yielded instead;
		  else a general Repetition pattern.
		  This is managed in Repetition's __new__ method. '''
	# example: 	(x/y)*
	# --> 		repetition:[choice:[name:x  name:y]  ZEROORMORE:*]
	# --> 		Repetition(x, numMin=False,numMax=False)
	# example: 	[1..9]{1..3}
	# --> 		repetition:[klass:[1..9]  numRanj:[1  3]]
	# --> 		Repetition(Klass("123456789"), numMin=1,numMax=3)
	# --> 		String(Klass("123456789"), numMin=1,numMax=3)
	#
	# original format expr for pattern output
	expr = repr(node.snippet)
	# repeted pattern, repetition suffix
	(pattern,suffix) = (node[0].value,node[1].value)
	# new node value
	node.value = "Repetition(%s, %s, expression=%s)" \
					% (pattern, suffix, expr)

def lookaheadCode(node):
	''' Change lookahead node value to lookahead expr. '''
	# example: 	!"foo"
	# --> 		nextNot:Word("foo")
	# --> 		NextNot(Word("foo"))
	#
	# next or nextNot?
	lookaheadTyp = "Next" if node.tag == "next" else "NextNot"
	pattern = node.value
	# new node value
	# original format expr for pattern output
	expr = repr(node.snippet)
	node.value = "%s(%s, expression=%s)" % (lookaheadTyp,pattern,expr)

### combination: sequence & choice
def sequenceCode(node):
	''' Change sequence node value to Sequence() expr. '''
	# example: 	a (b/c)
	# --> 		sequence:[a  Choice(b, c)]
	# --> 		Sequence(a, Choice(b, c))
	#
	# new node value
	# original format expr for pattern output
	expr = repr(node.snippet)
	# collect wrapped patterns
	patterns = [p.value for p in node.value]
	argList = ", ".join(patterns)
	node.value = "Sequence([%s], expression=%s)" % (argList,expr)
def choiceCode(node):
	''' Change choice node value to Choice() expr. '''
	# example: 	(x y) / z
	# --> 		choice:[Sequence(x, y)  z]
	# --> 		Choice(Sequence(x, y), z)
	#
	# new node value
	# original format expr for pattern output
	expr = repr(node.snippet)
	# collect wrapped patterns
	patterns = [p.value for p in node.value]
	argList = ", ".join(patterns)
	node.value = "Choice([%s], expression=%s)" % (argList,expr)

### pattern definition
def nameCode(node):
	''' Record pattern that happens to be a single name
		as a Clone of the original pattern.
		~ This allows independant further process. '''
	# example: 	x
	# --> 		name:x
	# --> 		clone(x)
	#
#~ 	patName=expr= node.value
#~ 	node.value = "Clone(%s, expression=%s)" % (patName,expr)
	pass

def formatCode(node):
	''' Add original format to pattern type & argument.
		~ case format node of type 'name':
		  rewrite to expr of pattern copy. '''
	return

def transformCode(node):
	''' Change transform node to expr of transform.
		~ Ensure the node has a '' value case no transform.
		~ Flag as recursive if tagged. '''
	# example: 	join real
	# --> 		(join, real)
	# example: 	@ extract
	# --> 		(extract)   & 'isRecursive' flag
	#
	node.isRecursive = False
	# case NIL value (no transform)
	if node.value == Node.NIL:
		node.value = ""
	# case recursive tag and/or transforms required
	else:
		transforms = node.value
		# -- take care of possible RECURSIVE flag
		if len(transforms)>0 and transforms[0].tag=="RECURSIVE":
			del transforms[0]
			node.isRecursive = True
		# -- new node value
		if len(transforms) == 0:
			node.value = ""
		else:
			def dispatchExpression(name):
				return "toolset['%s']" % name
			transformNames = [tr.value for tr in transforms]
			transformList = ", ".join(map(dispatchExpression, transformNames))
			node.value = "(%s)" % transformList

def patternCode(node):
	''' Change pattern definition to pattern expr code:
		~ Append possible transforms.
		~ Flag it as recursive if ever.
		~ (Original format expr is already given in call).
		Note: This will be used for single pattern generation. '''
	# example: 	x y : join
	# --> 		pattern[format:Word('foo', '"foo"')  transforms:drop]
	# --> 		Word('foo', '"foo"')(drop)
	#
	# pattern definition: format, transforms
	(format,transform) = node
	node.isRecursive =  transform.isRecursive
	node.isName =  format.tag == "name"
	# store data to allow rewriting (with name) in patternDefCode
	(format,transform) = (format.value, transform.value)
	(node.format,node.transform) = (format,transform)
	# new node value
	node.value = "%s%s" % (format, transform)

def patternDefCode(node):
	''' Change pattern line node value to pattern binding code:
		~ Name pattern.
		~ Flag it as recursive if ever.
		~ Special case of name patterns: must be cloned. '''
	# example: 	pat : "foo" : join
	# --> 		patternLine[name:pat  Word('foo', '"foo"')(drop)]
	# --> 		pat = Word('foo', '"foo"')(drop)
	# example: 	pat : x/y : @
	# --> 		patternLine[name:pat  Choice(x, y, "x/y")]	<isRecursive flag>
	# --> 		pat **= Choice(x, y)
	#
	### collect data
	(name,pattern) = node
	name=node.name = name.value 		# used by definitionCode
	node.isRecursive =  pattern.isRecursive
	(format,transform) = (pattern.format,pattern.transform)
	# trick syntax for recursive pattern
	BIND = "**=" if node.isRecursive else "="

	### set node value
	# special case of cloned pattern
	if pattern.isName:
		print "name pattern format", format
		node.value = 	"%s %s Clone(%s, expression='%s', name='%s')%s" \
						% (name, BIND, format, format,name, transform)
	# ordinary case
	else:
		# ~ pattern def node holds pattern & transform, plus recursive flag
		# ~ format & transform are stored by pattern node
		format_ = format[:-1]			# to insert naming in arg list
		node.value = 	"%s %s %s, name='%s')%s" \
						% (name, BIND, format_,name, transform)

### "skip" lines
def commentCode(node):
	''' Change comment node value to comment line in code. '''
	# new node value
	pass
def blankLineCode(node):
	''' Change blank line node value to blank line in code. '''
	# new node value
	pass
### sections
# Note: ensure that optional sections (introducton, toolset, preprocess)
# have a value so that we do not need to further analyse grammar structure
def titleCode(node):
	''' Write title line and record id. '''
	node.id = node.value.strip()
	# new node value
	node.value = "### title: %s ###\n" % node.id

def introductionCode(node):
	''' Change introduction node value to introduction in code. '''
	# introduction node: [intro lines] or NIL
	# where intro lines are comment or blank lines
	#
	# record title
	for line in node:
		if line.tag == "title":
			node.title = line.id
			break
	# new node value
	introLines = '\n'.join(line.value for line in node.value)
	node.value = "%s\n\n" % introLines

def toolsetCode(node):
	''' Change toolset node value to toolset section in code.
		~ just copy sequence of func defs '''
	TOOLSET = "### TOOLSET ###\n"
	# new node value
	if node.value == Node.NIL:
		node.tag = "toolset"
		node.value = '''

'''
	else:
		toolsetLines = '\n    '.join(line.value for line in node.value)
		node.value = \
'''def toolset_from_grammar():
    """Return a map of toolset functions hard-coded into the grammar."""
%s

    return locals().copy()

toolset.update(toolset_from_grammar())\n''' % toolsetLines

	node.value += 'toolset.update(actions)\n\n'

### TODO: elaborate preprocess section
def preprocessCode(node):
	''' Change preprocess node value to preprocess section in code.
		~ just copy lines for now '''
	PREPROCESS = "### PREPROCESS ###\n"
	# new node value
	if node.value == Node.NIL:
		node.tag = "preprocess"
		node.value = ""
	else:
		preprocessLines = '\n'.join(line.value for line in node.value)
		node.value = "%s\n\n" % preprocessLines

def definitionCode(node):
 	''' Transform definition node into definition code
		& define top pattern. '''
	# Definition lines can be:
	# ~ pattern def
	# ~ comment
	# ~ blank line
	#
	# all definition lines
	defLines = [lineNode.value for lineNode in node]
	# pattern nodes & names
	patternNodes = [lineNode for lineNode in node
						if lineNode.tag == "patternDef"]
	patternNames = [lineNode.name for lineNode in patternNodes]
	# Search recursive patterns & add pseudo-definitions for them:
	# "pat = Recursive()"   at start of definition section.
	recursiveNames = [lineNode.name for lineNode in patternNodes
						if lineNode.isRecursive == True]
	for name in recursiveNames:
		recursiveLine = "%s = Recursive(name='%s')" % (name,name)
		defLines.insert(1, recursiveLine)
	if len(recursiveNames) > 0:
		recursiveHeader = '# recursive pattern(s)'
		defLines.insert(1, recursiveHeader)
	# top pattern name
	node.topPatternName = patternNames[-1]
	# new node value
	node.value = '\n'.join(defLines)

def headerCode(node):
 	''' Transform header node into headr code.
		~ Just a syntactic trick using "if True:"
		  to build an indented block. '''
	# example: 	<definition>
	# --> 		if true: # <definition>
	#
	# new node value
	HEADERHEAD = "###   "
	node.value = HEADERHEAD + node.value

### whole grammar
def grammarCode(node):
	''' Change grammar node value to whole grammar code. '''
	# grammar node: [introduction title definition]
	# Note: grammar node's (source) grammar is 'text' attribute ;-)
	#
	# grammar sections: intro? titleLine toolset? preprocess? definition
	(introduction,toolset,definition) = node
	# grammar's own title,
	# "top pattern" name (last one)
	# & original text (definition only)
	node.title = introduction.title
	node.topPatternName = definition.topPatternName
	node.definition = definition.snippet
	# new node value
	node.value = introduction.value + toolset.value + definition.value

# debug func used to display info on a failing pattern
def check(node):
	pass

