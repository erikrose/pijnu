# coding: utf8


''' Â© copyright 2009 Denis Derman
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
''' overall character constants

	implemented as 'Lits':
		a variation on Literal with .text attribute

	does not allow unicode characters -- as of now
		characters limited to single byte format
		8-bit characters according to utf8 = latin-1

	dependances:
		* uses chars -- and charset through it

	******************************************************************
	© copyright 2009 Denis Derman
	
    This file is part of 'pijnu'.

    'pijnu' is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Foobar: see the file called 'GPL'.
    If not, see <http://www.gnu.org/licenses/>.
	'''


from sys import exit as end, stderr as error
from pijnu.library.pattern import Pattern, Char

def typ(obj): return obj.__class__.__name__

if True:	# === characters literals =================================
	'''	Note: numerous signs have several names in different categories:
			ASTERISK / STAR / MULT == '*' (True)
		'''
	# newline
	LF,CR	= chars('\x0a\x0d')

	# whitespace
	TAB,SPACE,NON_BRK_SPACE = chars('\x09\x20\xa0')

	# escaping
	BACKSLASH = ESCAPE = Char('\\')

	# separators
	DOT,COMMA,COLON,SEMICOLON,APOSTROPH,DASH,UNDERLINE = chars(".,:;'-_")
	UNDERSCORE = UNDERLINE

	# delimitors
	L_PARENTHESIS, R_PARENTHESIS = chars('()')
	L_BRACKET,R_BRACKET =  chars('[]')
	L_BRACE, R_BRACE	= chars('{}')
	SINGLE_QUOTE	= Char("'")
	DOUBLE_QUOTE	= Char('"')	# don't rename this 'QUOTE' if you use char choices!...
	QUOTE1,QUOTE2 = chars("'"+'"')	# ... name conflict

	# operators
	PLUS,MINUS,MULT,DIV = chars('+-*/')
	NOT,AND,OR,XOR = chars("!&|^")
	MULTIPLICATION,DIVISION = chars('×÷')
	PLUS_OR_MINUS	= Char('±')
	POWER			= Char('^')
	LESS_THAN,GREATER_THAN = INFERIOR,SUPERIOR = chars('<>')
	EQUAL = Char('=')

	# diacritics
	GRAVE,CARET,UMLAUT,TILDE,	MACRON,ACUTE,CEDILLA\
					= chars("`^¨~") + [Char(175),Char(180),Char(184)]

	# random signs
	"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~¡¢£¤¥¦§¨©ª«¬­®¯°±²³´µ¶·¸¹º»¼½¾¿×÷"""
	(NUMBER,PERCENT,AMPERSAND,EXCLAMATION,QUESTION
	,ARROBAS,BAR,PARAGRAPH,ALINEA,ASTERISK,SLASH)\
					= chars('#%&!?@|¶§*/')
	STAR			= ASTERISK

	# delete -- special case
	DELETE			= Char("\x7f")

if True:	# === pattern naming =====================================
	for name,object in globals().items():
		if isinstance(object,Pattern):
			object.name = name

if True:	# === export ============================================
	# initial name lists
	# (categories initially are sequences)
	_char_names = 	[
			"ALINEA", "AMPERSAND", "APOSTROPH", "ARROBAS", "ASTERISK", "STAR",
			"BACKSLASH", "BAR", "COLON", "COMMA", "CR", "DELETE",
			"DASH", "DIV", "DOT", "ESCAPE", "EXCLAMATION",
			"GRAVE", "CARET", "UMLAUT", "TILDE", "MACRON", "ACUTE", "CEDILLA",
			"LESS_THAN", "GREATER_THAN", "INFERIOR", "SUPERIOR","EQUAL",
			"LF", "L_BRACE", "L_BRACKET", "L_PARENTHESIS",
			"MULTIPLICATION", "DIVISION",
			"NOT", "AND", "OR", "XOR",
			"MINUS", "MULT", "NON_BRK_SPACE", "NUMBER",
			"PARAGRAPH", "PERCENT", "PLUS_OR_MINUS", "PLUS", "POWER",
			"QUESTION", "SINGLE_QUOTE", "DOUBLE_QUOTE", "QUOTE1", "QUOTE2",
			"R_BRACE", "R_BRACKET", "R_PARENTHESIS",
			"SEMICOLON", "SLASH", "SPACE", "TAB", "UNDERLINE","UNDERSCORE"
					]
	_char_names.sort()
	# export names
	CHARS_names = __all__ = _char_names + ["CHARS_names"]



# === info / test ===================================================
if __name__ == '__main__': # show what will be exported
	if True:	# export name list check
		_names	= [n for n in dir() if not n[0]=='_']
		_consts	= [n for n in _names if n.isupper()]
		_chars = list(_char_names)

		print "\ncardinal check: %s=%s?" %(len(_consts),len(_chars))
		print "set check: _consts=_chars ? %s" % (_consts == _chars)
		print "missing names: %s" % [n for n in _consts if n not in _chars]
		print "names too much: %s" % [n for n in _chars if n not in  _consts]
		if 	(
			len(_consts) != len(_chars)
			or
			_consts != _chars
			):
			print "\n_chars: %s\n%s" %(len(_chars),_chars)
			print "_consts: %s\n%s" %(len(_consts),_consts)

	if True:	# name list
		print "\n=== export name list -- sorted ===\n"
		print "char names\n%s\n" %_char_names

	if True:	# character list
		print "\n==========================================="
		print "\n\n=== characters ==="
		for name in _char_names:
			char = globals()[name].char
			if name in ['SPACE','TAB','LF','CR','DELETE']:
				char = repr(char)
			print "%-15s%s" % (name,char)


