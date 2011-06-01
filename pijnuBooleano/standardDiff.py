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
'''
	Create language specific-grammar from
	* standard Booleano grammar
	* current differential config
	by updating the former from the latter.
	
	~ The diff config must be given as argument and
	  is copied into currentConfig.pijnu so that
	  the differential parser can process it.
	
	~ The parser for the standard config reads all grammar,
	  updates patterns from the diff config and returns
	  a representation of the new grammar.
	'''

from pijnu.generator import writeParser

def createGrammar(source_filename="testlang.pijnu"):
	# copy current diff config file into currentConfig.pijnu
	source = file(source_filename).read
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
	standard_diff_grammar = file("standardBooleanoDiff.pijnu").read()
	writeParser(standard_diff_grammar)
	from standardBooleanoDiffParser.py import standardBooleanoDiffParser as p
	standard_grammar = file("standardBooleano").read()
	lang_grammar = p.parse(standard_grammar)
	
	# Write it to file.
	# (Destination filename is built from source filename.)
	lang_name = source_filename.split('.')[0]
	dest_filename = "%sBooleano.pijnu" % lang_name
	dest_file = file(dest_filename, 'w')
	dest_file.write(lang_grammar)
	dest_file.close()
	
