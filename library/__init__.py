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
'''		p i j n u   l i b r a r y
	
	client interface to export useful names
	
	dependance structure:
	
	pijnu
		tools.py (used everywhere)
		library
			parser.py
			pattern.py
				node.py (includes builtin transform funcs)
				error.py (pijnu exception classes)
				charset.py (parse Klass expression)
			preprocess.py
			CHARS.py
			CLASSES.py
			
		generator <-- lib
	'''

### import/export
# pattern imports node & error
from pattern import *			# pattern types & match methods
from parser import Parser		# Parser object
from preprocess import *		# builtin preprocessing funcs

# modules below not 100% safe as of now
# -- maybe will be cancelled
#~ from CHARS import *				# constant Char patterns
#~ from CLASSES import *			# constant Klass patterns
