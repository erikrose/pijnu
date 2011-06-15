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
SEP			: ' '
DOT			: '.'
digit		: [0..9]
integer		: digit+
real		: integer DOT integer?
number		: real / integer
numbers		: number (SEP number)*


"""

from pijnu import *

### title: noTransform ###
###   <toolset>
def toReal(node):
	node.value = float(node.value)

###   <definition>
SEP = Char(' ', format="' '")
DOT = Char('.', format="'.'")
digit = Klass(format='[0..9]', charset='0123456789')
integer = Repetition(digit, numMin=1,numMax=False, format='digit+')
real = Sequence([integer, DOT, Option(integer, format='integer?')], format='integer DOT integer?')
number = Choice([real, integer], format='real / integer')
numbers = Sequence([number, Repetition(Sequence([SEP, number], format='SEP number'), numMin=False,numMax=False, format='(SEP number)*')], format='number (SEP number)*')

noTransformParser = Parser(vars(), 'numbers', 'noTransform', 'None')

