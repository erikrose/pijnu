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
SEP			: ' '						: drop
DOT			: '.'
digit		: [0..9]
integer		: digit+					: join
real		: integer DOT integer?		: join
number		: real / integer			: toReal
addedNum	: SEP number				: liftNode
numbers		: number (addedNum)*		: extract

"""



from pijnu.library import *

numbersTransformParser = Parser()
state = numbersTransformParser.state



### title: numbersTransform ###
###   <toolset>
def toReal(node):
	node.value = float(node.value)

###   <definition>
SEP = Char(' ', format="' '")(drop)
DOT = Char('.', format="'.'")
digit = Klass(format='[0..9]', charset='0123456789')
integer = Repetition(digit, numMin=1,numMax=False, format='digit+')(join)
real = Sequence([integer, DOT, Option(integer, format='integer?')], format='integer DOT integer?')(join)
number = Choice([real, integer], format='real / integer')(toReal)
addedNum = Sequence([SEP, number], format='SEP number')(liftNode)
numbers = Sequence([number, Repetition(copy(addedNum), numMin=False,numMax=False, format='(addedNum)*')], format='number (addedNum)*')(extract)



numbersTransformParser._recordPatterns(vars())
numbersTransformParser._setTopPattern("numbers")
numbersTransformParser.grammarTitle = "numbersTransform"
numbersTransformParser.fileName = "numbersTransformParser.py"
