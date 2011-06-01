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
'''		p i j n u command-line parser generator
	
	command line parser generation
	
	call format:
		pythno gen.py grammar_file_name  [parser_file_name]
	
	If parser_file_name is not given, the parser is written into
		grammar_title + "Parser.py"

	'''

### import/export
from pijnu.generator import makeParser
from sys import argv as arguments
from pijnu.tools import *

def do():
	''' write parser from grammar '''
	# get source grammar from command line argument
	try:
		grammar = file(arguments[1],'r').read()
	except IndexError:
		message = (	"\nCall Format:\n"
					"\tpython gen.py grammar_file_name\n"
					"or\n"
					"\tpython gen.py grammar_file_name  parser_file_name\n\n"
					)
		write(message)
		end()
	# write parser into target file -- maybe specified
	try:
		parserFile = file(arguments[2],'w')
		writeParser(grammar, parserFile)
	except Exception:
		writeParser(grammar)

if __name__ == "__main__":
	do()
