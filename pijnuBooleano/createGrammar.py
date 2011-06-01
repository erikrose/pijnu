# -*- coding:utf-8 -*-


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
'''	language-specific grammar creation
	
	Create new language-specific-grammar from
	* standard Booleano grammar
	* current differential config
	by updating the former from the latter.
	
	~ The diff config must be given as argument and
	  is copied into currentConfig.pijnu so that
	  the config parser can process it.
	
	~ The parser for the standard config reads all grammar,
	  updates patterns from the diff config, and joins back.
	'''

from pijnu.generator import writeParser

def createGrammar(lang):
	# copy current diff config file into currentConfig.pijnu
	source_filename = "%s.pijnu" % lang
	source = file(source_filename).read()
	current_config = file("currentConfig.pijnu", 'w')
	current_config.write(source)
	current_config.close()
	
	### parse & process standard Booleano grammar
	# This standard grammar parser first launches parsing of
	# the currentConfig to build a dict of new patterns.
	# Then, it automagically uses these definitions to
	# replace patterns *while* parsing the standard grammar.
	# So that we get an abstract representation of a new grammar:
	# just need to write it properly into a new grammar file.
	
	# Build new grammar.
	# (temporary rewrite parser for testing)
	standard_diff_grammar = file("standardDiff.pijnu").read()
	writeParser(standard_diff_grammar)
	from standardDiffParser import standardDiffParser as parser
	standard_grammar = file("standard.pijnu").read()
	lang_grammar = parser.parse(standard_grammar).value

	# Write it to file.
	# (Destination filename is built from source filename.)
	lang_name = source_filename.split('.')[0]
	dest_filename = "%sBooleano.pijnu" % lang_name
	dest_file = file(dest_filename, 'w')
	dest_file.write(lang_grammar)
	dest_file.close()

def getParser(lang):
	''' Create a language-specific grammar,
		parse and process it into a parser,
		return this parser.
		~ The user should pass a language name
		  for which a 'lang.pijnu' file exists. '''
	import sys
	# write new language-specific grammar
	createGrammar(lang)
	grammar_filename = "%sBooleano.pijnu" % lang
	# write language-specific parser module
	grammar = file(grammar_filename).read()
	parser_filename = "%sBooleanoParser.py" % lang
	writeParser(grammar, filename=parser_filename)
	# get language-specific parser object
	parser_name = "%sBooleanoParser" % lang
#~ 	from parser_name import parser_name as parser
	parserModule = __import__(parser_name)
	langParser = parserModule.langParser
	return langParser

def test(parser, tests):
	from pijnu.library import PijnuError
	# read test suite list of source expressions
	lines = open(tests).readlines()
	sources = [l.strip() for l in lines]
	sources = [l for l in sources if l != ""]
	sources = [l for l in sources if not l.startswith('#')]
	d = parser.testSuiteDict(sources)
	# just to test method 'testSuite'
	parser.testSuite(d)

if __name__ == "__main__":
	# A language name should be passed as 1st arg,
	# else 'testlang' will be used.
	# A test suite file name should be passed as 2nd arg,
	# else 'testtests' will be used.
	import sys
	try:
		lang = sys.argv[1]
		try:
			tests = sys.argv[2]
		except IndexError:
			tests = 'testtests'
	except IndexError:
		lang = "testlang"
		tests = 'testtests'
	parser = getParser(lang)
	test(parser, tests)
