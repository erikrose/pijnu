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

'''
Pijnu meta-parser
'''

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
	SPACING			: (TAB / SPC)*
	# end of line
	LF				: '\x0a'
	CR				: '\x0d'
	NL				: (CR LF) / LF / CR
	TRAIL			: SPACING
	EOL				: TRAIL (LF / CR)+					: drop
	# syntax codes
	DOT				: '.'
	SLASH			: '/'
	# column
	COLON			: ':'
	ALIGN			: SPACING
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
	tagging				: STARPATTERN? SPC? RECURSIVE? SPC?
	transformName		: IDENTIFIER
	moreTransform		: SPC transformName						: liftNode
	moreTransforms		: moreTransform*
	transformCall		: tagging transformName? moreTransforms	: extract
### TODO: add line continuation (backslash EOL)
# pattern: name, format, transform
	patName			: IDENTIFIER
	formatCol		: COLUMN format								: liftNode
	transformCol	: COLUMN transformCall						: liftNode
	###pattern		: formatCol transformCol? 					: patternCode
	patternDef 	: SPACING patName formatCol transformCol? EOL	: patternDefCode
# skip line: blank & comment
	blankLine		: SPACING EOL									: liftValue
	commentLine		: SPACING COMMENT INLINETEXT EOL				: join commentCode
	skipLine		: blankLine / commentLine
# config parameter
### TODO: add preprocessing & toolset
# sections
	headerName		: IDENTIFIER
	header			: SPACING headerName EOL
	blockStart		: SPACING BLOCKSTART EOL						: drop
	blockEnd		: SPACING BLOCKEND EOL						: drop
	notBlockEnd		: !blockEnd
	block			: BLOCKSTART VALIDCHAR BLOCKEND
# preprocessing
# toolset	: custom transform, validation, preprocess functions
	#toolsetHeader	: SPACING SECTION SPC? "toolset"
	toolsetLine		: !blockEnd SPACING INLINETEXT EOL			: join
	toolsetBLock	: toolsetLine+
	toolset			: blockStart toolsetBLock blockEnd
### TODO: indented block structure
# title line
	title			: IDENTIFIER
	titleLine		: SPACING title EOL							: liftNode
# whole grammar
	introduction	: skipLine*									: introductionCode
	defLine			: patternDef / skipLine
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

from pijnu.library import *
from pijnuActions import *
# pijnu meta grammar
# title: grammar
group = Recursive()
if True:	### tokens
	## separators -- delimitors
	# spacing
	SPACING = String(Klass(" \t"),numMin=0)(join)
	DROPSPACING = String(Klass(" \t"),numMin=0)(drop)
	INDENT = Clone(SPACING)
	DROPINDENT = Clone(DROPSPACING)
	# end of line
	NL = Char('\n')
	EOL = Sequence( [ DROPSPACING, NL ] )(drop)
	# column
	COLON = Char(':')
	COLUMN = Sequence([SPACING, COLON, SPACING])(drop)
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
	LGROUP = Sequence([LPAREN, DROPSPACING])(drop)
	RGROUP = Sequence([DROPSPACING, RPAREN])(drop)
	SEQUENCE = String(Klass(" \t"),numMin=1)(drop)
	CHOICE = Choice([ Sequence([DROPSPACING, SLASH, DROPSPACING]), SLASH ])(drop)
	# various
	COMMENT = Char('#')
	RECURSIVE = Char('@')

	## character classes
	DECDIGIT = Klass(r'0..9')
	HEXDIGIT = Klass(r'0..9abcdefABCDEF')
	IDSTART = Klass(r'a..z  A..Z  _')
	IDSUITE = Klass(r'a..z  A..Z  0..9  _')
	# VALIDCHAR: ASCII only for now: 'black' chars + sp tab nl cr
	VALIDCHAR = Klass(r'\x21..\x7e  \x20\x09\x0a\x0d')
	# SAFECHAR: exclude backslash "'" '"' ']'
	SAFECHAR = Klass(r'\x21..\x7e  \x20\x09\x0a\x0d  !!\x22\x27\x5c\x5d')
	# chars to encode special & unsafe characters: t r n ' " backslash ]
	CODECHAR = Klass(r'[trn  \x22\x27\x5c\x5d]')
	# INLINECHAR for comment: 'black' chars + sp + tab
	INLINECHAR = Klass(r'\x21..\x7e  \x20\x09')

	## character strings
	INTEGER = String(DECDIGIT)
	IDENTIFIER = Sequence([IDSTART, String(IDSUITE,numMin=0)])(join)
	INLINETEXT = String(INLINECHAR,numMin=0)(join)

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
	name = copy(IDENTIFIER)(join,nameCode)
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
	repetSuffix	= Choice([numRepete, ZEROORMORE, ONEORMORE])(repetSuffixCode)
#~ 	stringRepetition = Sequence([klass, repetSuffix])(stringCode)
#~ 	genRepetition = Sequence([item, repetSuffix])(repetitionCode)
#~ 	repetition = Choice([stringRepetition, genRepetition])
	repetition = Sequence([item, repetSuffix])(repetitionCode)
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
	moreChoice = Sequence([CHOICE, term])
	moreChoices = ZeroOrMore(moreChoice)
	choice = Sequence([term, CHOICE, term, ZeroOrMore(Sequence([CHOICE, term]))])(extract,extract, choiceCode)
	# format <--> group
	format = Choice([choice, sequence, term])(formatCode)
	group **= Sequence([LGROUP, format, RGROUP])(liftNode)
	# transformation
	recursiveTag 	= Sequence([Option(RECURSIVE), DROPSPACING])
	transformName 	= copy(IDENTIFIER)
	moreTransform 	= Sequence([DROPSPACING, transformName])(liftNode)
	moreTransforms 	= ZeroOrMore(moreTransform)
	transformCall 	= Sequence([recursiveTag, Option(transformName), moreTransforms])(extract)
	optTransform 	= Option(transformCall)(transformCode)

if True:	### grammar structure
	## line types
	#== TODO: line continuation (...EOL)
	#== TODO: config parameter
	## pattern line: name, format, transform
	patName 		= copy(IDENTIFIER)
	# Note: 'pattern' will be used for single pattern generation
	# 		and used (like a regex pattern) with match methods. '''
	### FIXME: there could be 2 ':' between format and transform
	pattern			= Sequence([format, OPTCOLUMN, optTransform])(patternCode)
	patternDef 	= Sequence([DROPSPACING, patName, COLUMN, pattern, EOL])(patternDefCode)

	## section/block/header/body meta pattern
	LHEADER			= Char('<')
	RHEADER			= Char('>')
	headerName 		= copy(IDENTIFIER)
	header 			= Sequence([INDENT, LHEADER, headerName, RHEADER, EOL])(join)
	notHeader		= NextNot(header)

	## skip line: blank, comment
	blankLine 		= Sequence([INDENT, EOL])(liftValue)
	commentLine 	= Sequence([INDENT, COMMENT, INLINETEXT, EOL])(join)
	skipLine 		= Choice([blankLine, commentLine])

	## introduction with title & free comment
	titleID			= copy(IDENTIFIER)
	title	 		= Sequence([DROPINDENT, titleID, EOL])(join,titleCode)
	introLine 		= Choice([title, skipLine])
	introduction	= OneOrMore(introLine)(introductionCode)


	## toolset: custom transform, validation, & preprocess functions
	TOOLSET			= Word("toolset")
	toolsetHeader	= Sequence([INDENT, LHEADER, TOOLSET, RHEADER, EOL])(join,headerCode)
	toolsetLine 	= Sequence([notHeader, INDENT, INLINETEXT, EOL])(join)
	toolsetLines 	= ZeroOrMore(toolsetLine)
#~ 	toolsetBLock	= Sequence([blockStart, toolsetLines, blockEnd)(extract)
	toolset 		= Sequence([toolsetHeader, toolsetLines])(extract,liftValue)
	optToolset 		= Option(toolset)(toolsetCode)

	## definition: sequence of patterns
	DEFINITION		= Word("definition")
	definitionHeader= Sequence([INDENT, LHEADER, DEFINITION, RHEADER, EOL])(join,headerCode)
	definitionLine	= Choice([patternDef, skipLine])
	definitionLines	= ZeroOrMore(definitionLine)
#~ 	definitionBLock	= Recursive()
#~ 	definitionItem	= Choice([definitionBLock, definitionLine)
#~ 	definitionItems	= OneOrMore(definitionItem)(definitionItemsCode)
#~ 	definitionBLock	**= Sequence([blockStart, definitionItems, blockEnd)(extract)
	definition		= Sequence([definitionHeader, definitionLines])(extract,definitionCode)

	## whole grammar:
	# introduction & toolset? & preprocess? & definition
	# where toolset is optional
	grammar 		= Sequence	([
								introduction,
								optToolset,
								definition
								])(grammarCode)


### parser object ###
pijnuParser = Parser(locals(), 'grammar', "pijnu", "pijnuParser.py")

