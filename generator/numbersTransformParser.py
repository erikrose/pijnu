""" numbersTransform
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

numbersTransformParser = Parser()
state = numbersTransformParser.state



### title: numbersTransform ###


###   <toolset>
def doAdd(node):
    (n1,n2) = (node[0].value,node[1].value)
    node.value = int(n1) + int(n2)

###   <definition>
# constants
SEP = Char(' ', expression="' '",name='SEP')(drop)
ADD = Char('+', name='ADD')
# operand
digit = Klass('0123456789', expression='[0..9]',name='digit')
integer = Repetition(digit, numMin=1,numMax=False, expression='digit+',name='integer')(join)
# operation
addition = Sequence([integer, ADD, integer], name="addition")(doAdd)



numbersTransformParser._recordPatterns(vars())
numbersTransformParser._setTopPattern("numbers")
numbersTransformParser.grammarTitle = "numbersTransform"
numbersTransformParser.filename = "numbersTransformParser.py"
