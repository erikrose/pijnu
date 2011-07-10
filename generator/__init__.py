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
Pijnu generator

Client interface to export useful names

Structure:

pijnu
    generator <-- library
        generator (write parser -- yield pattern)
        pijnuparser.py (pijnu meta parser)
        pijnu.pijnu (pijnu meta grammar)
        pijnuActions.py (specific transformations)
'''

### import/export
from generator import makeParser, getPattern, fileText
