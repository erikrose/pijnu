# coding: utf8

'''		p i j n u   g e n e r a t o r
	
	client interface to export useful names
	
	structure:
	
	pijnu
		generator <-- library
			generator (write parser -- yield pattern)
			pijnuparser.py (pijnu meta parser)
			pijnu.pijnu (pijnu meta grammar)
			pijnuToolset.py (specific transformations)
	

	'''

### import/export
from generator import makeParser, getPattern, fileText
