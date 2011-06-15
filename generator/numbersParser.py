""" numbers
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
SPACE   : ' '
POINT   : '.'
digit   : [0..9]
integer : digit+
real    : integer POINT integer?
number  : real / integer
numbers : number (SPACE number)*

"""



from pijnu.library import *

numbersParser = Parser()
state = numbersParser.state



### title: numbers ###


###   <definition>
SPACE = Char(' ', expression="' '",name='SPACE')
POINT = Char('.', expression="'.'",name='POINT')
digit = Klass('0123456789', expression='[0..9]',name='digit')
integer = Repetition(digit, numMin=1,numMax=False, expression='digit+',name='integer')
real = Sequence([integer, POINT, Option(integer, expression='integer?')], expression='integer POINT integer?',name='real')
number = Choice([real, integer], expression='real / integer',name='number')
numbers = Sequence([number, Repetition(Sequence([SPACE, number], expression='SPACE number'), numMin=False,numMax=False, expression='(SPACE number)*')], expression='number (SPACE number)*',name='numbers')



numbersParser._recordPatterns(vars())
numbersParser._setTopPattern("numbers")
numbersParser.grammarTitle = "numbers"
numbersParser.filename = "numbersParser.py"
