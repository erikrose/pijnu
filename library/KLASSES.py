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
### TODO: update to newer version of pijnu

''' overall character klass constants

	* built on lists of character Literals from module CHARS
	* character alternations are pyparsing Regex objects
	(previously MatchFirst)
	* does not allow unicode characters -- as of now
		characters limited to single byte format
		8-bit characters according to utf8 = latin-1
	'''

from sys import exit as end, stderr as error
#from pyparsing import oneOf#, MatchFirst
from pijnu.library.pattern import Pattern, Klass
from CHARS import *
_start_names = dir()

# call CharChoice with "

if True:	# === characters classes ==================================
	# newline
	NL_CHAR 		= CharChoice(LF,CR)

	# whitespace
	WHITE_CHAR		= CharChoice(TAB,SPACE,NON_BRK_SPACE)

	# separators
	SEPARATOR		= 	CharChoice(DOT,COMMA,COLON,SEMICOLON, \
						APOSTROPH,DASH,UNDERLINE)

	# delimitors
	PARENTHESIS = ROUND_BRACE = CharChoice(L_PARENTHESIS,R_PARENTHESIS)
	BRACKET = SQUARE_BRACE = CharChoice(L_BRACKET,R_BRACKET)
	BRACE = CURLY_BRACE = CharChoice(L_BRACE,R_BRACE)
	QUOTE			= CharChoice(QUOTE1,QUOTE2)
	DELIMITOR		= QUOTE | PARENTHESIS | BRACKET | BRACE

	# operators
	ARITHMETIC_OPERATOR = CharChoice(PLUS,MINUS,MULT,DIV)
	LOGIC_OPERATOR	= CharChoice(NOT,AND,OR,XOR)
	OPERATOR		= ARITHMETIC_OPERATOR | LOGIC_OPERATOR

	# diacritics
	DIACRITIC		= CharChoice(GRAVE,CARET,UMLAUT,TILDE,MACRON,ACUTE,CEDILLA)

	# all signs
	# [ sign == !(special | invalid | newline | whitespace | letter | digit)
	# [ sign == (operator | delimitor | separator | many others)
	SIGN	 	= 	CharChoice	(
								r"\033..\047  \058..\064  \091..\096  \123..\126"
								+
								r"\161..\191  \215\247"
								)

	# digits
	DEC_DIGIT		= CharChoice("0..9")
	HEX_DIGIT		= DEC_DIGIT | CharChoice("A..F a..f")

	# letters
	ASCII_LOWER		= CharChoice("a..z")
	ASCII_UPPER		= CharChoice("A..Z")
	ASCII_LETTER	= ASCII_LOWER | ASCII_UPPER
	LATIN_LETTER	= CharChoice(r"\192..\214  \216..\246  \248..\255")
	LETTER			= ASCII_LETTER | LATIN_LETTER

	# usually unused chars
	# note: chr(0) actually is a perfectly valid char,
	# but it bugs C under-layer of CPython
	# [ print "%s%s%s" %(chr(65),chr(0),chr(67)) ==> A (should be AC)
	SPECIAL_CHAR	= CharChoice(r"\001..\008  \011..\012  \014..\031"
								, DELETE)
	CONTROL_CHAR	= CharChoice(r"\001..\031", DELETE)
	INVALID_CHAR	= CharChoice(r"\000  \128..\159")

	# major collections
	INVISIBLE_CHAR	= WHITE_CHAR | NL_CHAR			# usual ! black
	BLACK_CHAR		= SIGN | DEC_DIGIT | LETTER		# ~ visible
	INLINE_CHAR		= BLACK_CHAR | WHITE_CHAR		# ~ ! control
	USUAL_CHAR		= INLINE_CHAR | NL_CHAR			# everyday fodder
	VALID_CHAR		= INLINE_CHAR | CONTROL_CHAR	# (except chr(0))

	# ascii / latin-1
	ASCII_INLINE_CHAR	= CharChoice(r"\032..\126")
	LATIN_INLINE_CHAR	= CharChoice(r"\161..\255")

if True:	# === pattern naming =====================================
	for name,object in globals().items():
		if isinstance(object,Pattern):
			object.name = name

if True:	# === export ============================================
	# initial name lists
	# (categories initially are sequences)
	_choice_names = [
		"DEC_DIGIT","HEX_DIGIT",
		"ARITHMETIC_OPERATOR","LOGIC_OPERATOR","OPERATOR",
		"BRACE","BRACKET","PARENTHESIS",
		"ROUND_BRACE","SQUARE_BRACE","CURLY_BRACE",
		"QUOTE","DELIMITOR","SEPARATOR","DIACRITIC","SIGN",
		"ASCII_LOWER","ASCII_UPPER","ASCII_LETTER","LATIN_LETTER","LETTER",
		"BLACK_CHAR","WHITE_CHAR","NL_CHAR","INVISIBLE_CHAR",
		"ASCII_INLINE_CHAR","LATIN_INLINE_CHAR","INLINE_CHAR",
		"USUAL_CHAR","VALID_CHAR",
		"SPECIAL_CHAR","CONTROL_CHAR","INVALID_CHAR"
					]
	# export names
	CHAR_CHOICES_names = __all__ = _choice_names + ["CHAR_CHOICES_names"]

# === info ========================================================
if __name__ == "__main__": # show what will be exported
	if True:	# export name list check
		_names	= [n for n in dir() if not n[0]=="_"]
		_S_consts	= [n for n in _names
					if (n.isupper() and not n in _start_names)]
		_choices = list(_choice_names)
		_choices.sort()
		# length and name list check
		print "\ncardinal check: %s=%s?" % (len(_S_consts),len(_choices))
		print "set check: _S_consts=_choices ? %s" % (_S_consts == _choices)
		print "missing names: %s" % [n for n in _S_consts if n not in _choices]
		print "names too much: %s" % [n for n in _choices if n not in _S_consts]
		# list output if check not passed
		if 	(
			len(_S_consts) != len(_choices)
			or
			_S_consts != _choices
			):
			print "_choices: %s\n%s" %(len(_choices),_choices)
			print "_S_consts: %s\n%s" %(len(_S_consts),_S_consts)

	if True:	# name list
		print "\n=== export name list -- sorted ===\n"
		print "sequence names\n%s\n" %_choices

	if True:	# content list
		print "\n==========================================="
		print "\n\n=== char choices/classes ~ classified ===\n"
		for name in _choice_names:
			obj = globals()[name]
			# case of invalid chars (skip chr(0))
			if name == "INVALID_CHAR":
				print 	"invalid chars:\n[%s]" \
						% ",".join(repr(c) for c in obj.string)
				obj = obj-chr(0)
			print "%s\n%s\n" % (name,obj.string)


