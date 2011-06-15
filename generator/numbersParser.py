""" numbers
<definition>
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
