"""
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
		## separators
			# spacing
			# SPACES is a token for Sequence and in transform column.
			# OPTSPACE is for convenience inside formats.
			# BLANK (includes tabs) is allowed outside formats only.
			SPACE			: ' '
			OPTSPACE		: SPACE								: drop
			SPACES			: SPACE+
			TAB				: '\x09'
			BLANK			: (TAB / SPACE)*					: drop
			INDENT			: BLANK
			TRAIL			: BLANK
			ALIGN			: BLANK
			# columns
			COLON			: ':'
			COLUMN			: ALIGN COLON ALIGN					: drop
			# end of line
			LF				: '\x0a'
			CR				: '\x0d'
			NL				: (CR LF) / LF / CR
			EOL				: TRAIL NL							: drop
			# character coding
			ESCAPE			: '\x5c'
		## codes
			# character expression for: char, word, ranj, klass
			# (no need to drop codes as there will be transformation anyway)
			CODEDCHAR		: ESCAPE
			DECCHAR			: ESCAPE
			HEXCHAR			: ESCAPE 'x'
			EXCLUSION		: "!!"
			RANJ			: ".."
			KLASSSEP		: "  "								: drop
			CHAR			: "\'"								: drop
			WORD			: "\""								: drop
			LCLAS			: "["								: drop
			RCLAS			: "\]"								: drop
			ANYCHAR			: "."
			# term affix -- no spacing allowed
			# (do not drop repetition suffix)
			ZEROORMORE		: "+"
			ONEORMORE		: "+"
			LREPETE			: '{'								: drop
			RREPETE			: '}'								: drop
			NUMRANJ			: ".."								: drop
			OPTION			: '?'								: drop
			NEXT			: '&'								: drop
			NEXTNOT			: '!'								: drop
			# major pattern combination
			LGROUP			: OPTSPACE "(" OPTSPACE				: drop
			RGROUP			: OPTSPACE ")" OPTSPACE				: drop
			CHOICE			: OPTSPACE "/" OPTSPACE				: drop
			SEQUENCE		: SPACES							: drop
			# structure
			LHEADER			: "<"
			RHEADER			: ">"
			TRANSFORMSEP	: SPACES							: drop
			RECURSIVE		: "@"
			COMMENT			: "#"
		## character classes
			DECDIGIT		: [0..9]
			HEXDIGIT		: [0..9  abcdef  ABCDEF]
			IDSTART			: [a..z  A..Z  _]
			IDSUITE			: [a..z  A..Z  0..9  _]
			# ASCII only for now: 'black' chars + sp tab nl cr
			VALIDCHAR		: [\x21..\x7e  \x20\x09\x0a\x0d]
			# exclude backslash "'" '"' ']'
			SAFECHAR		: [\x21..\x7e  \x20\x09\x0a\x0d  !!\x22\x27\x5c\x5d]
			# chars to encode special & unsafe characters: t r n ' " backslash ]
			CHARCODE		: [trn  \x22\x27\x5c\x5d]
			# for comment and toolset: 'black' chars + sp + tab
			INLINECHAR		: [\x21..\x7e  \x20\x09]
		## character strings
			INTEGER			: DECDIGIT+
			IDENTIFIER		: IDSTART IDSUITE*							: join
			INLINETEXT		: INLINECHAR+								: join
		
	### pattern format definition
		## character expression (inside user specific grammar)
			# codedChar: TAB LF CR backslash ] ' "
			codedChar		: CODEDCHAR CHARCODE						: liftValue codeToChar
			# hex/dec ordinal code
			hexChar			: HEXCHAR HEXDIGIT HEXDIGIT					: join hexToChar
			decChar			: DECCHAR DECDIGIT DECDIGIT DECDIGIT		: join decToChar
			# literal: safe char only
			litChar			: SAFECHAR
			charExpr		: codedChar / hexChar / decChar / litChar
			ranj			: charExpr RANJ charExpr					: ranjToCharset
		## item: group, klass, word, char, named pattern
			# @@@ group recursion here @@@
			namedPattern	: IDENTIFIER
			char			: CHAR charExpr CHAR						: liftValue charCode
			charExprs		: charExpr+									: join
			word			: WORD charExprs WORD						: liftValue wordCode
			klassItem		: ranj / EXCLUSION / KLASSSEP / charExpr
			klass			: LCLAS klassItem+ RCLAS					: liftValue klassCode
			item			: group / klass / word / char / namedPattern
		## affix term: lookahead, option, repetition
			# option
			option			: item OPTION								: optionCode
			# numbered repetition {n} or {m..n}
			number			: INTEGER
			numRanj			: number NUMRANJ number
			numbering		: numRanj / number
			numRepete		: LREPETE numbering RREPETE					: liftNode
			# repetition -- with special case of string
			repetSuffix		: numRepete / ZEROORMORE / ONEORMORE
			stringRepetition: klass repetSuffix
			genRepetition	: item repetSuffix
			repetition		: stringRepetition / genRepetition			: repetitionCode
			# lookahead
			lookSuite		: repetition / option / item
			lookahead		: (NEXT / NEXTNOT) lookSuite				: liftValue lookaheadCode
			# item --> term
			term			: lookahead / repetition / option / item
		## format: term combination
			# @@@  group>format>term>item>   circular recursion @@@
			# combination
			sequence		: term SEQUENCE term (SEQUENCE term)*		: intoList sequenceCode
			choice			: term CHOICE term (CHOICE term)*			: intoList choiceCode
			# format <--> group
			format			: choice / sequence / term					: formatCode
			group			: LGROUP format RGROUP						: @ liftNode
		## transformation column -- including recursive tag
			transformName	: IDENTIFIER
			transformCalls	: transformName (TRANSFORMSEP transformName)*	: intoList
			recursiveTag	: (RECURSIVE TRANSFORMSEP)?					: liftNode
			transforms		: recursiveTag transformCalls				: extract
		## pattern: patternName format transforms
			patternName		: IDENTIFIER
			formatCol		: COLUMN format								: liftNode
			transformCol	: COLUMN transforms							: liftNode
			optTransform	: transformCol?								: transformCode
			pattern			: formatCol optTransform 					: patternCode
			patternLine		: INDENT patternName pattern				: patternLineCode
		
	### grammar structure
		#== TODO: add line continuation (backslash EOL) ???
		#== TODO: config parameter
		## meta pattern for grammar sections
			headerName 		: IDENTIFIER
			header 			: BLANK LHEADER headerName RHEADER EOL		: join
			notHeader		: !header
		## skip line: blank, comment
			blankLine		: INDENT EOL								: join
			commentLine		: INDENT COMMENT INLINETEXT EOL				: join
			skipLine		: blankLine / commentLine
		## free introduction
			introduction	: skipLine+
			optIntroduction	: introduction?								: introductionCode
		## title
			titleID			: IDENTIFIER
			title			: (INDENT titleID EOL)?						: join titleCode
		## toolset: custom transform, validation, & preprocess functions
			TOOLSET			: "toolset"
			toolsetHeader	: INDENT LHEADER TOOLSET RHEADER EOL 		: join headerCode
			toolsetLine		: notHeader INDENT INLINETEXT EOL			: join
			toolsetBLock	: toolsetLine+
			toolset			: toolsetHeader toolsetBLock				: extract
			optToolset		: toolset?									: toolsetCode
		## definition: sequence of patterns
			DEFINITION		: "definition"
			definitionHeader: INDENT LHEADER DEFINITION RHEADER EOL 	: join headerCode
			definitionLine	: patternLine / skipLine
			definitionBLock	: definitionLine+
			definition		: definitionHeader definitionBLock			: extract definitionCode
		## whole grammar:
			# introduction & title & toolset & definition
			# where introduction & toolset are optional
			grammar	: optIntroduction title optToolset definition		: grammarCode




"""



from pijnu.library import *

pijnuParser = Parser()
state = pijnuParser.state



# pijnu meta grammar

### title: pijnu ###
###   <toolset>
	from pijnuToolset import *

###   <preprocess>
	#

###   <definition>
# recursive pattern(s)
group = Recursive()
	### tokens
		## separators
			# spacing
			# SPACES is a token for Sequence and in transform column.
			# OPTSPACE is for convenience inside formats.
			# BLANK (includes tabs) is allowed outside formats only.
SPACE = Char(' ', format="' '")
OPTSPACE = copy(SPACE)(drop)
SPACES = Repetition(SPACE, numMin=1,numMax=False, format='SPACE+')
TAB = Char('\t', format="'\\x09'")
BLANK = Repetition(Choice([TAB, SPACE], format='TAB / SPACE'), numMin=False,numMax=False, format='(TAB / SPACE)*')(drop)
INDENT = copy(BLANK)
TRAIL = copy(BLANK)
ALIGN = copy(BLANK)
			# columns
COLON = Char(':', format="':'")
COLUMN = Sequence([ALIGN, COLON, ALIGN], format='ALIGN COLON ALIGN')(drop)
			# end of line
LF = Char('\n', format="'\\x0a'")
CR = Char('\r', format="'\\x0d'")
NL = Choice([Sequence([CR, LF], format='CR LF'), LF, CR], format='(CR LF) / LF / CR')
EOL = Sequence([TRAIL, NL], format='TRAIL NL')(drop)
			# character coding
ESCAPE = Char('\\', format="'\\x5c'")
		## codes
			# character expression for: char, word, ranj, klass
			# (no need to drop codes as there will be transformation anyway)
CODEDCHAR = copy(ESCAPE)
DECCHAR = copy(ESCAPE)
HEXCHAR = Sequence([ESCAPE, Char('x', format="'x'")], format="ESCAPE 'x'")
EXCLUSION = Word('!!', format='"!!"')
RANJ = Word('..', format='".."')
KLASSSEP = Word('  ', format='"  "')(drop)
CHAR = Word("'", format='"\\\'"')(drop)
WORD = Word('"', format='"\\""')(drop)
LCLAS = Word('[', format='"["')(drop)
RCLAS = Word(']', format='"\\]"')(drop)
ANYCHAR = Word('.', format='"."')
			# term affix -- no spacing allowed
			# (do not drop repetition suffix)
ZEROORMORE = Word('+', format='"+"')
ONEORMORE = Word('+', format='"+"')
LREPETE = Char('{', format="'{'")(drop)
RREPETE = Char('}', format="'}'")(drop)
NUMRANJ = Word('..', format='".."')(drop)
OPTION = Char('?', format="'?'")(drop)
NEXT = Char('&', format="'&'")(drop)
NEXTNOT = Char('!', format="'!'")(drop)
			# major pattern combination
LGROUP = Sequence([OPTSPACE, Word('(', format='"("'), OPTSPACE], format='OPTSPACE "(" OPTSPACE')(drop)
RGROUP = Sequence([OPTSPACE, Word(')', format='")"'), OPTSPACE], format='OPTSPACE ")" OPTSPACE')(drop)
CHOICE = Sequence([OPTSPACE, Word('/', format='"/"'), OPTSPACE], format='OPTSPACE "/" OPTSPACE')(drop)
SEQUENCE = copy(SPACES)(drop)
			# structure
LHEADER = Word('<', format='"<"')
RHEADER = Word('>', format='">"')
TRANSFORMSEP = copy(SPACES)(drop)
RECURSIVE = Word('@', format='"@"')
COMMENT = Word('#', format='"#"')
		## character classes
DECDIGIT = Klass(format='[0..9]', charset='0123456789')
HEXDIGIT = Klass(format='[0..9  abcdef  ABCDEF]', charset='0123456789abcdefABCDEF')
IDSTART = Klass(format='[a..z  A..Z  _]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_')
IDSUITE = Klass(format='[a..z  A..Z  0..9  _]', charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')
			# ASCII only for now: 'black' chars + sp tab nl cr
VALIDCHAR = Klass(format='[\\x21..\\x7e  \\x20\\x09\\x0a\\x0d]', charset='!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ \t\n\r')
			# exclude backslash "'" '"' ']'
SAFECHAR = Klass(format='[\\x21..\\x7e  \\x20\\x09\\x0a\\x0d  !!\\x22\\x27\\x5c\\x5d]', charset='!#$%&()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[^_`abcdefghijklmnopqrstuvwxyz{|}~ \t\n\r')
			# chars to encode special & unsafe characters: t r n ' " backslash ]
CHARCODE = Klass(format='[trn  \\x22\\x27\\x5c\\x5d]', charset='trn"\'\\]')
			# for comment and toolset: 'black' chars + sp + tab
INLINECHAR = Klass(format='[\\x21..\\x7e  \\x20\\x09]', charset='!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~ \t')
		## character strings
INTEGER = Repetition(DECDIGIT, numMin=1,numMax=False, format='DECDIGIT+')
IDENTIFIER = Sequence([IDSTART, Repetition(IDSUITE, numMin=False,numMax=False, format='IDSUITE*')], format='IDSTART IDSUITE*')(join)
INLINETEXT = Repetition(INLINECHAR, numMin=1,numMax=False, format='INLINECHAR+')(join)
		
	### pattern format definition
		## character expression (inside user specific grammar)
			# codedChar: TAB LF CR backslash ] ' "
codedChar = Sequence([CODEDCHAR, CHARCODE], format='CODEDCHAR CHARCODE')(liftValue, codeToChar)
			# hex/dec ordinal code
hexChar = Sequence([HEXCHAR, HEXDIGIT, HEXDIGIT], format='HEXCHAR HEXDIGIT HEXDIGIT')(join, hexToChar)
decChar = Sequence([DECCHAR, DECDIGIT, DECDIGIT, DECDIGIT], format='DECCHAR DECDIGIT DECDIGIT DECDIGIT')(join, decToChar)
			# literal: safe char only
litChar = copy(SAFECHAR)
charExpr = Choice([codedChar, hexChar, decChar, litChar], format='codedChar / hexChar / decChar / litChar')
ranj = Sequence([charExpr, RANJ, charExpr], format='charExpr RANJ charExpr')(ranjToCharset)
		## item: group, klass, word, char, named pattern
			# @@@ group recursion here @@@
namedPattern = copy(IDENTIFIER)
char = Sequence([CHAR, charExpr, CHAR], format='CHAR charExpr CHAR')(liftValue, charCode)
charExprs = Repetition(charExpr, numMin=1,numMax=False, format='charExpr+')(join)
word = Sequence([WORD, charExprs, WORD], format='WORD charExprs WORD')(liftValue, wordCode)
klassItem = Choice([ranj, EXCLUSION, KLASSSEP, charExpr], format='ranj / EXCLUSION / KLASSSEP / charExpr')
klass = Sequence([LCLAS, Repetition(klassItem, numMin=1,numMax=False, format='klassItem+'), RCLAS], format='LCLAS klassItem+ RCLAS')(liftValue, klassCode)
item = Choice([group, klass, word, char, namedPattern], format='group / klass / word / char / namedPattern')
		## affix term: lookahead, option, repetition
			# option
option = Sequence([item, OPTION], format='item OPTION')(optionCode)
			# numbered repetition {n} or {m..n}
number = copy(INTEGER)
numRanj = Sequence([number, NUMRANJ, number], format='number NUMRANJ number')
numbering = Choice([numRanj, number], format='numRanj / number')
numRepete = Sequence([LREPETE, numbering, RREPETE], format='LREPETE numbering RREPETE')(liftNode)
			# repetition -- with special case of string
repetSuffix = Choice([numRepete, ZEROORMORE, ONEORMORE], format='numRepete / ZEROORMORE / ONEORMORE')
stringRepetition = Sequence([klass, repetSuffix], format='klass repetSuffix')
genRepetition = Sequence([item, repetSuffix], format='item repetSuffix')
repetition = Choice([stringRepetition, genRepetition], format='stringRepetition / genRepetition')(repetitionCode)
			# lookahead
lookSuite = Choice([repetition, option, item], format='repetition / option / item')
lookahead = Sequence([Choice([NEXT, NEXTNOT], format='NEXT / NEXTNOT'), lookSuite], format='(NEXT / NEXTNOT) lookSuite')(liftValue, lookaheadCode)
			# item --> term
term = Choice([lookahead, repetition, option, item], format='lookahead / repetition / option / item')
		## format: term combination
			# @@@  group>format>term>item>   circular recursion @@@
			# combination
sequence = Sequence([term, SEQUENCE, term, Repetition(Sequence([SEQUENCE, term], format='SEQUENCE term'), numMin=False,numMax=False, format='(SEQUENCE term)*')], format='term SEQUENCE term (SEQUENCE term)*')(intoList, sequenceCode)
choice = Sequence([term, CHOICE, term, Repetition(Sequence([CHOICE, term], format='CHOICE term'), numMin=False,numMax=False, format='(CHOICE term)*')], format='term CHOICE term (CHOICE term)*')(intoList, choiceCode)
			# format <--> group
format = Choice([choice, sequence, term], format='choice / sequence / term')(formatCode)
group **= Sequence([LGROUP, format, RGROUP], format='LGROUP format RGROUP')(liftNode)
		## transformation column -- including recursive tag
transformName = copy(IDENTIFIER)
transformCalls = Sequence([transformName, Repetition(Sequence([TRANSFORMSEP, transformName], format='TRANSFORMSEP transformName'), numMin=False,numMax=False, format='(TRANSFORMSEP transformName)*')], format='transformName (TRANSFORMSEP transformName)*')(intoList)
recursiveTag = Option(Sequence([RECURSIVE, TRANSFORMSEP], format='RECURSIVE TRANSFORMSEP'), format='(RECURSIVE TRANSFORMSEP)?')(liftNode)
transforms = Sequence([recursiveTag, transformCalls], format='recursiveTag transformCalls')(extract)
		## pattern: patternName format transforms
patternName = copy(IDENTIFIER)
formatCol = Sequence([COLUMN, format], format='COLUMN format')(liftNode)
transformCol = Sequence([COLUMN, transforms], format='COLUMN transforms')(liftNode)
optTransform = Option(transformCol, format='transformCol?')(transformCode)
pattern = Sequence([formatCol, optTransform], format='formatCol optTransform')(patternCode)
patternLine = Sequence([INDENT, patternName, pattern], format='INDENT patternName pattern')(patternLineCode)
		
	### grammar structure
		#== TODO: add line continuation (backslash EOL) ???
		#== TODO: config parameter
		## meta pattern for grammar sections
headerName = copy(IDENTIFIER)
header = Sequence([BLANK, LHEADER, headerName, RHEADER, EOL], format='BLANK LHEADER headerName RHEADER EOL')(join)
notHeader = NextNot(header, format='!header')
		## skip line: blank, comment
blankLine = Sequence([INDENT, EOL], format='INDENT EOL')(join)
commentLine = Sequence([INDENT, COMMENT, INLINETEXT, EOL], format='INDENT COMMENT INLINETEXT EOL')(join)
skipLine = Choice([blankLine, commentLine], format='blankLine / commentLine')
		## free introduction
introduction = Repetition(skipLine, numMin=1,numMax=False, format='skipLine+')
optIntroduction = Option(introduction, format='introduction?')(introductionCode)
		## title
titleID = copy(IDENTIFIER)
title = Option(Sequence([INDENT, titleID, EOL], format='INDENT titleID EOL'), format='(INDENT titleID EOL)?')(join, titleCode)
		## toolset: custom transform, validation, & preprocess functions
TOOLSET = Word('toolset', format='"toolset"')
toolsetHeader = Sequence([INDENT, LHEADER, TOOLSET, RHEADER, EOL], format='INDENT LHEADER TOOLSET RHEADER EOL')(join, headerCode)
toolsetLine = Sequence([notHeader, INDENT, INLINETEXT, EOL], format='notHeader INDENT INLINETEXT EOL')(join)
toolsetBLock = Repetition(toolsetLine, numMin=1,numMax=False, format='toolsetLine+')
toolset = Sequence([toolsetHeader, toolsetBLock], format='toolsetHeader toolsetBLock')(extract)
optToolset = Option(toolset, format='toolset?')(toolsetCode)
		## definition: sequence of patterns
DEFINITION = Word('definition', format='"definition"')
definitionHeader = Sequence([INDENT, LHEADER, DEFINITION, RHEADER, EOL], format='INDENT LHEADER DEFINITION RHEADER EOL')(join, headerCode)
definitionLine = Choice([patternLine, skipLine], format='patternLine / skipLine')
definitionBLock = Repetition(definitionLine, numMin=1,numMax=False, format='definitionLine+')
definition = Sequence([definitionHeader, definitionBLock], format='definitionHeader definitionBLock')(extract, definitionCode)
		## whole grammar:
			# introduction & title & toolset & definition
			# where introduction & toolset are optional
grammar = Sequence([optIntroduction, title, optToolset, definition], format='optIntroduction title optToolset definition')(grammarCode)



pijnuParser._recordPatterns(vars())
pijnuParser._setTopPattern(grammar)
pijnuParser.grammarTitle = "pijnu"
pijnuParser.fileName = "pijnuParser1.py"
