""" addition
<definition>
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

additionParser = Parser()
state = additionParser.state



### title: addition ###


###   <toolset>
def doAdd(node):
    (n1,n2) = (node[0].value,node[1].value)
    node.value = int(n1) + int(n2)

###   <definition>
# constants
SEP = Char(' ', expression="' '",name='SEP')(drop)
ADD = Char('+', name='ADD')(drop)
# operand
digit = Klass('0123456789', expression='[0..9]',name='digit')
integer = Repetition(digit, numMin=1,numMax=False, expression='digit+',name='integer')(join)
# operation
addition = Sequence([integer, ADD, integer], name="addition")#(doAdd)



additionParser._recordPatterns(vars())
additionParser._setTopPattern("addition")
additionParser.grammarTitle = "addition"
additionParser.filename = "additionParser.py"
