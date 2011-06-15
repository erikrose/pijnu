"""# pijnu meta grammar
	grammar
# separators
	# comment
	HASH			: '#'
	# spacing
	SPC				: ' '								: drop
	SPC2			: "  "								: drop
	SPC3			: "   "								: drop
	SPACING			: SPC+								: drop
	TAB				: '\x09'							: drop
	BLANK			: (TAB / SPC)*
	# end of line
	LF				: '\x0a'
	CR				: '\x0d'
	NL				: (CR LF) / LF / CR
	TRAIL			: BLANK
	EOL				: TRAIL (LF / CR)+					: drop
	# syntax codes
	DOT				: '.'
	SLASH			: '/'
	# column
	COLON			: ':'
	ALIGN			: BLANK
	COLUMN			: ALIGN COLON ALIGN					: drop
	AT				: '@'
	STAR			: '*'
	PLUS			: '+'
	SECTION			: "###"
	BLOCKSTART		: '{'
	BLOCKEND		: '}'
	# character coding
	ESC				: '\x5c'
# codes
	COMMENT			: HASH								: drop
	RECURSIVE		: AT
	STARPATTERN		: STAR
	# character expression: char, word, ranj, class
	# (no need to drop coding as it will be transformed anyway)
	CHARCODE		: ESC
	DEC				: ESC
	HEX				: ESC "x"
	RANJ			: ".."
	EXCLUSION		: "!!"
	CHAR			: "\'"								: drop
	WORD			: "\""								: drop
	LKLASS			: "["								: drop
	RKLASS			: "\]"								: drop
	# term affix
	# (do not drop repetition suffix)
	ZEROORMORE		: STAR
	ONEORMORE		: PLUS
	LREPETE			: "{"								: drop
	RREPETE			: "}"								: drop
	UNTIL			: ">"								: drop
	OPTION			: "?"								: drop
	NEXT			: "&"								: drop
	NEXTNOT			: "!"								: drop
	# major combination
	LGROUP			: "( " / "("						: drop
	RGROUP			: " )" / ")"						: drop
	SEQUENCE		: SPC3 / SPC2 / SPC					: drop
	CHOICE			: (SPC SLASH SPC) / SLASH			: drop
# character classes
	DECDIGIT		: [0..9]
	HEXDIGIT		: [0..9  abcdef  ABCDEF]
	IDSTART			: [a..z  A..Z  _]
	IDSUITE			: [a..z  A..Z  0..9  _]
	# ASCII only for now: 'black' chars + sp tab nl cr
	VALIDCHAR		: [\x21..\x7e  \x20\x09\x0a\x0d]
	# exclude backslash "'" '"' ']'
	SAFECHAR		: [\x21..\x7e  \x20\x09\x0a\x0d  !!\x22\x27\x5c\x5d]
	# chars to encode special & unsafe characters: t r n ' " backslash ]
	CODECHAR		: [trn  \x22\x27\x5c\x5d]
	# for comment: 'black' chars + sp + tab
	INLINECHAR		: [\x21..\x7e  \x20\x09]
# character strings
	INTEGER			: DECDIGIT+
	IDENTIFIER		: IDSTART IDSUITE*							: join
	INLINETEXT		: INLINECHAR+
# character expression (inside user specific grammar)
	# codedChar: TAB LF CR backslash ] ' "
	codedChar		: CHARCODE CODECHAR							: liftValue codeToChar
	# char hex/dec ordinal liftValue
	hexChar			: HEX HEXDIGIT HEXDIGIT						: join hexToChar
	decChar			: DEC DECDIGIT DECDIGIT DECDIGIT			: join decToChar
	# literal: safe char only
	litChar			: SAFECHAR
	charExpr		: codedChar / hexChar / decChar / litChar
	ranj			: charExpr RANJ charExpr					: ranjToCharset
# item: class, word, char, name
	### group recursive here
	name			: IDENTIFIER
	char			: CHAR charExpr CHAR						: liftValue charCode
	word			: WORD charExpr+ WORD						: liftValue wordCode
	klassItem		: ranj / charExpr / EXCLUSION / SPC2
	klass			: LKLASS klassItem+ RKLASS					: liftValue klassCode
	item			: group / klass / word / char / name
	### TODO: extend affixes to any kind of item (not only name)
	### TODO: introduce string	: klass klass? ('*'/'+'/numbering)
# affix term: lookahead, option, repetition + until
	# option
	option			: item OPTION								: optionCode
	# numbered repetition {n} or {m, n}
	number			: INTEGER
	numRanj			: number RANJ number
	numbering		: numRanj / number
	numRepet		: LREPETE numbering RREPETE					: liftNode
	# repetition...
	repetSuffix		: numRepet / ZEROORMORE / ONEORMORE
	baseRepet		: item (repetSuffix)						: baseRepetCode
	# ...with possible until stop condition
	until			: UNTIL item								: liftNode
	untilRepet		: baseRepet until							: untilRepetCode
	repetition		: untilRepet / baseRepet
	# lookahead
	lookSuite		: repetition / option / item
	next			: NEXT lookSuite
	nextNot			: NEXTNOT lookSuite
	lookahead		: (nextNot / next) 							: liftValue lookaheadCode
	# item --> term
	term			: lookahead / repetition / option / item
# format: term combination
	# --   group>format>term>item>   circular recursive
	# combination
	moreSeq			: SEQUENCE term								: liftNode
	moreSeqs		: moreSeq*
	sequence		: term SEQUENCE term moreSeqs				: extract sequenceCode
	moreChoice		: CHOICE term								: liftNode
	moreChoices		: moreChoice*
	choice			: term CHOICE term moreChoices				: extract choiceCode
	# format <--> group
	format			: choice / sequence / term					: formatCode
	group			: LGROUP format RGROUP						: @ liftNode
# transformation
	tagging			: STARPATTERN? SPC? RECURSIVE? SPC?
	transformName	: IDENTIFIER
	moreTransform	: SPC transformName							: liftNode
	moreTransforms	: moreTransform*
	transformCall	: tagging transformName? moreTransforms		: extract
### TODO: add line continuation (backslash EOL)
# pattern: name format transform
	patName			: IDENTIFIER
	formatCol		: COLUMN format								: liftNode
	transformCol	: COLUMN transformCall						: liftNode
	###pattern		: formatCol transformCol? 					: patternCode
	patternLine 	: BLANK patName formatCol transformCol? EOL	: patternDefCode
# skip line: blank & comment
	blankLine		: BLANK EOL									: liftValue
	commentLine		: BLANK COMMENT INLINETEXT EOL				: join commentCode
	skipLine		: blankLine / commentLine
# config parameter
### TODO: add preprocessing & toolset
# section meta-pattern
	headerName		: IDENTIFIER
	header			: BLANK headerName EOL
	blockStart		: BLANK BLOCKSTART EOL						: drop
	blockEnd		: BLANK BLOCKEND EOL						: drop
	notBlockEnd		: !blockEnd
	block			: BLOCKSTART VALIDCHAR BLOCKEND
# preprocessing
# toolset	: custom transform, validation, preprocess functions
	#toolsetHeader	: BLANK SECTION SPC? "toolset"
	toolsetLine		: !blockEnd BLANK INLINETEXT EOL			: join
	toolsetBLock	: toolsetLine+
	toolset			: blockStart toolsetBLock blockEnd
### TODO: indented block structure
# title line
	title			: IDENTIFIER
	titleLine		: BLANK title EOL							: liftNode
# whole grammar
	introduction	: skipLine*									: introductionCode
	defLine			: patternLine / skipLine
	#definition		: blockStart defLine+ blockEnd				: definitionCode
	definition		: defLine+ 									: definitionCode
	grammar			: introduction titleLine? definition toolset? block?: * grammarCode

{
def charCode(node):
	''' Change char node value to Char() expression. '''
	# example: 	'a'
	# --> 		char:'a'
	# --> 		Char('a')
	# use repr() to avoid trouble of control characters
	char = repr(node.value)
	# new node value
	node.value = "Char" + LPAREN + char + RPAREN

def wordCode(node):
	''' Change word node value to Word() expression. '''
	# example: 	"xyz"
	# --> 		word:"xyz"
	# --> 		Word("xyz")
	# 
	# use repr() to avoid trouble of control characters
	word = repr(node.value)
	# new node value
	node.value =  "Word" + LPAREN + word + RPAREN

def klassCode(node):
	''' Change klass node value to Klass() expression. '''
	# example: 	[a..e  0..9  _ -  !!d0]
	# --> 		klass:"a..e  0..9  _ -  !!d0"
	# --> 		klass:"abcde0123456789_ -!!d0"	(rangeToCharset)
	# --> 		klass:"abce123456789_ -"		(klassToCharset)
	# --> 		Klass("abce123456789_ -")		(klassCode)
	# A class node can hold: range, "!!" EXCLUSION code, "  " SPC2 separator,
	# single character expression (litChat, codedChar, decChar, hexChar)
	# Apply klassToCharset transformation
	klassToCharset(node)
	# use repr() to avoid trouble of control characters
	charset = repr(node.value)
	# new node value
	node.value = "Klass" + LPAREN + charset + RPAREN
}


"""

from pijnu import *
from pijnuToolset import *
# pijnu meta grammar
# title: grammar
group = Recursive()
if True:	### tokens
	## separators -- delimitors
	# space & tab
	SPACE = Char(' ')
	OPTSPACE = Option(SPACE)(drop)
	TAB = Char('\t')
	WHITE = Klass(" \t")
	BLANK = ZeroOrMore(WHITE)(join)
	DROPBLANK = ZeroOrMore(WHITE)(drop)
	# end of line
	LF = Char('\n')
	CR = Char('\r')
	NL = Choice([Sequence([CR, LF]), LF, CR])
	EOL = Sequence( [ DROPBLANK, OneOrMore(Choice([LF, CR])) ] )(drop)
	# column
	COLON = Char(':')
	COLUMN = Sequence([BLANK, COLON, BLANK])(drop)
	OPTCOLUMN = Option(COLUMN)(drop)
	# structure
	BLOCKSTART = Char('{')
	BLOCKEND = Char('}')
	# syntax
	SLASH = Char('/')
	LPAREN = Char('(')
	RPAREN = Char(')')
	ESC = Char('\\')
	
	## codes
	# character expression: char, word, ranj, class
	# (no need to drop escape as code will be transformed anyway)
	CHARCODE = copy(ESC)
	DEC = copy(ESC)
	HEX = Sequence([ESC, Char('x')])
	CHAR = Char('\'')(drop)
	WORD = Char('"')(drop)
	CHARRANJ = Word('..')(drop)
	KLASSSEP = Word('  ')(drop)
	EXCLUSION = Word('!!')
	LKLASS = Char('[')(drop)
	RKLASS = Char(']')(drop)
	NUMRANJ = Word('..')(drop)
	ANYCHAR = Char('.')
	# term affix
	# (do not drop repetition suffix)
	ZEROORMORE = Char('*')
	ONEORMORE = Char('+')
	LREPETE = Char('{')(drop)
	RREPETE = Char('}')(drop)
	OPTION = Char('?')(drop)
	NEXT = Char('&')(drop)
	NEXTNOT = Char('!')(drop)
	# major combination
	LGROUP = Sequence([LPAREN, OPTSPACE])(drop)
	RGROUP = Sequence([OPTSPACE, RPAREN])(drop)
	SEQUENCE = OneOrMore(SPACE)(drop)
	CHOICE = Choice([ Sequence([OPTSPACE, SLASH, OPTSPACE]), SLASH ])(drop)
	# various
	COMMENT = Char('#')
	RECURSIVE = Char('@')
	
	## character classes
	DECDIGIT = Klass(r'0..9', '0123456789')
	HEXDIGIT = Klass(r'0..9abcdefABCDEF', '0123456789abcdefABCDEF')
	IDSTART = Klass(r'a..z  A..Z  _', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
	IDSUITE = Klass(r'a..z  A..Z  0..9  _', 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
	# VALIDCHAR: ASCII only for now: 'black' chars + sp tab nl cr
	VALIDCHAR = Klass(r'\x21..\x7e  \x20\x09\x0a\x0d','!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ \t\n\r')
	# SAFECHAR: exclude backslash "'" '"' ']'
	SAFECHAR = Klass(r'\x21..\x7e  \x20\x09\x0a\x0d  !!\x22\x27\x5c\x5d', '!#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[^_`abcdefghijklmnopqrstuvwxyz{|}~ \t\n\r')
	# chars to encode special & unsafe characters: t r n ' " backslash ]
	CODECHAR = Klass(r'[trn  \x22\x27\x5c\x5d', 'trn"\'\\]')
	# INLINECHAR for comment: 'black' chars + sp + tab
	INLINECHAR = Klass(r'\x21..\x7e  \x20\x09', '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ \t')

	## character strings
	INTEGER = OneOrMore(DECDIGIT)
	IDENTIFIER = Sequence([IDSTART, ZeroOrMore(IDSUITE)])(join)
	INLINETEXT = OneOrMore(INLINECHAR)(join)

if True:	### pattern definition
	## character expression in user specific grammar
	# codedChar: TAB LF CR backslash ] ' "
	codedChar = Sequence([CHARCODE, CODECHAR])(join, liftValue, codeToChar)
	# char hex/dec ordinal liftValue
	hexChar = Sequence([HEX, HEXDIGIT, HEXDIGIT])(join, hexToChar)
	decChar = Sequence([DEC, DECDIGIT, DECDIGIT, DECDIGIT])(join, decToChar)
	# literal: safe char only
	litChar = copy(SAFECHAR)
	charExpr = Choice([codedChar, hexChar, decChar, litChar])
	charRanj = Sequence([charExpr, CHARRANJ, charExpr])(ranjToCharset)
	# item: class, word, char, name
	name = copy(IDENTIFIER)
	char = Sequence([CHAR, charExpr, CHAR])(liftValue, charCode)
	charExprs = OneOrMore(charExpr)(join)
	word = Sequence([WORD, charExprs, WORD])(liftValue, wordCode)
	klassItem = Choice([charRanj, EXCLUSION, KLASSSEP, charExpr])
	klass = Sequence([LKLASS, OneOrMore(klassItem), RKLASS])(join, liftValue, klassToCharset, klassCode)
	#@@ group recursion here @@
	item = Choice([group, klass, word, char, name])
	
	## affix term: lookahead, option, repetition
	# option
	option = Sequence([item, OPTION])(optionCode)
	# numbered repetition {n} or {m..} or {m..n}
	number = copy(INTEGER)(join)
	numRanj = Sequence([number, NUMRANJ, number])
	numbering = Choice([numRanj, number])
	numRepete = Sequence([LREPETE, numbering, RREPETE])(liftNode)
	# repetition -- special case of string
	repetSuffix	= Choice([numRepete, ZEROORMORE, ONEORMORE])
	stringRepetition = Sequence([klass, repetSuffix])
	genRepetition = Sequence([item, repetSuffix])
	repetition = Choice([stringRepetition, genRepetition])(repetitionCode)
	# lookahead
	lookSuite = Choice([repetition, option, item])
	next = Sequence([NEXT, lookSuite])
	nextNot = Sequence([NEXTNOT, lookSuite])
	lookahead = Choice([nextNot, next])(liftValue, lookaheadCode)
	# item --> term
	term = Choice([lookahead, repetition, option, item])
	
	## format: term combination
	# group>format>term>item>   circular recursion
	# combination
	moreSeq = Sequence([SEQUENCE, term])(liftNode)
	moreSeqs = ZeroOrMore(moreSeq)
	sequence = Sequence([term, SEQUENCE, term, moreSeqs])(extract, sequenceCode)
	moreChoice = Sequence([CHOICE, term])(liftNode)
	moreChoices = ZeroOrMore(moreChoice)
	choice = Sequence([term, CHOICE, term, moreChoices])(extract, choiceCode)
	# format <--> group
	format = Choice([choice, sequence, term])(formatCode)
	group **= Sequence([LGROUP, format, RGROUP])(liftNode)
	# transformation
	recursiveTag = Sequence([Option(RECURSIVE), OPTSPACE])
	transformName = copy(IDENTIFIER)
	moreTransform = Sequence([OPTSPACE, transformName])(liftNode)
	moreTransforms = ZeroOrMore(moreTransform)
	transformCall = Sequence([recursiveTag, Option(transformName), moreTransforms])(extract)

if True:	### grammar structure
	## line types
	#== TODO: line continuation (...EOL)
	#== TODO: config parameter
	## pattern line: name, format, transform
	patName 		= copy(IDENTIFIER)
	optTransform 	= Option(transformCall)(transformCode)
	# Note: 'pattern' will be used for single pattern generation
	# 		and used (like a regex pattern) with match methods. '''
	### FIXME: there could be 2 ':' between format and transform
	pattern			= Sequence([format, OPTCOLUMN, optTransform])(patternCode)
	patternLine 	= Sequence([DROPBLANK, patName, COLUMN, pattern, EOL])(patternLineCode)
	
	## section meta pattern
	LHEADER			= Char('<')
	RHEADER			= Char('>')
	headerName 		= copy(IDENTIFIER)
	header 			= Sequence([BLANK, LHEADER, headerName, RHEADER, EOL])(join)
	notHeader		= NextNot(header)
	
	## skip line: blank, comment
	blankLine 		= Sequence([BLANK, EOL])(liftValue)
	commentLine 	= Sequence([BLANK, COMMENT, INLINETEXT, EOL])(join, commentCode)
	skipLine 		= Choice([blankLine, commentLine])###, blockWrap)
	
	## free introduction
	introduction	= OneOrMore(skipLine)
	optIntroduction	= Option(introduction)(introductionCode)

	## title
	titleID			= copy(IDENTIFIER)
	title	 		= Sequence([DROPBLANK, titleID, EOL])(join,titleCode)

	## toolset: custom transform, validation, & preprocess functions
	TOOLSET			= Word("toolset")
	toolsetHeader	= Sequence([BLANK, LHEADER, TOOLSET, RHEADER, EOL])(join,headerCode)
	toolsetLine 	= Sequence([notHeader, BLANK, INLINETEXT, EOL])(join)
	toolsetLines 	= ZeroOrMore(toolsetLine)
	toolset 		= Sequence([toolsetHeader, toolsetLines])(extract)
	optToolset 		= Option(toolset)(toolsetCode)

	## definition: sequence of patterns
	DEFINITION		= Word("definition")
	definitionHeader= Sequence([BLANK, LHEADER, DEFINITION, RHEADER, EOL])(join,headerCode)
	definitionLine	= Choice([patternLine, skipLine])
	definitionLines	= ZeroOrMore(definitionLine)
	definition		= Sequence([definitionHeader, definitionLines])(extract,definitionCode)

	## whole grammar:
	# introduction & title & toolset & preprocess & definition
	# where introduction & toolset & preprocess are optional
	grammar 		= Sequence	([
								optIntroduction,
								title,
								optToolset,
								definition
								])(grammarCode)


### parser object ###
pijnuParser = Parser(locals(), 'grammar', "pijnu", "pijnuParser0.py")

########### test changes ############
#~ text = r"""'\\' '\t' '\n' '\r' '\'' '\"' '\]'"""
#~ char.test(text, "findAll")
#~ text = r"""'\x09' '\x20' '\x61'"""
#~ char.test(text, "findAll")
#~ text = r"""'\009' '\032' '\097'"""
#~ char.test(text, "findAll")
#~ 
#~ text = r"""[a..e  0..9  *+  !!c0..6]"""
#~ klass.test(text)
###
#~ text = r"""[0..9]"""
#~ k = klass.match(text)
#~ print k
#~ digit,digit.name = eval(k.value),'digit'
#~ print digit
#~ print digit.findAll("123.45 ")
###
text = """\
[a..b]?
[a..b]*
[a..b]+
[a..b]{3}
[a..b]{3..}
[a..b]{3..7}
[a..b]{..7}
"a--b"?
"a--b"*
"a--b"+
"a--b"{3}
"a--b"{3..}
"a--b"{3..7}
"a--b"{..7}
"""
#~ repetition.test(text,"findAll")
