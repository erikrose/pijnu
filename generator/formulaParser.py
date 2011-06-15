""" formula
<definition>
digit		: [0..9.]
number		: digit+										: join toReal
ADD			: '+'											: drop
MULT		: '*'											: drop
LPAREN		: '('											: drop
RPAREN		: ')'											: drop
mult		: (grup/number) MULT (grup/mult/number)			: @
add			: (grup/mult/number) ADD (grup/add/mult/number) : @
grup		: LPAREN (add / mult) RPAREN					: @ liftNode
formula		: add / mult / digit

"""



from pijnu.library import *

formulaParser = Parser()
state = formulaParser.state



### title: formula ###


###   <toolset>
def doAdd(node):
	(n1,n2) = (node[0].value,node[1].value)
	node.value = n1 + n2
def doMult(node):
	(n1,n2) = (node[0].value,node[1].value)
	node.value = n1 * n2

###   <definition>
# recursive pattern(s)
grup = Recursive(name='grup')
add = Recursive(name='add')
mult = Recursive(name='mult')
digit = Klass('0123456789.', expression='[0..9.]',name='digit')
number = Repetition(digit, numMin=1,numMax=False, expression='digit+',name='number')(join, toReal)
ADD = Char('+', expression="'+'",name='ADD')(drop)
MULT = Char('*', expression="'*'",name='MULT')(drop)
LPAREN = Char('(', expression="'('",name='LPAREN')(drop)
RPAREN = Char(')', expression="')'",name='RPAREN')(drop)
mult **= Sequence([Choice([grup, number], expression='grup/number'), MULT, Choice([grup, mult, number], expression='grup/mult/number')], expression='(grup/number) MULT (grup/mult/number)',name='mult')
add **= Sequence([Choice([grup, mult, number], expression='grup/mult/number'), ADD, Choice([grup, add, mult, number], expression='grup/add/mult/number')], expression='(grup/mult/number) ADD (grup/add/mult/number)',name='add')
grup **= Sequence([LPAREN, Choice([add, mult], expression='add / mult'), RPAREN], expression='LPAREN (add / mult) RPAREN',name='grup')(liftNode)
formula = Choice([add, mult, digit], expression='add / mult / digit',name='formula')



formulaParser._recordPatterns(vars())
formulaParser._setTopPattern("formula")
formulaParser.grammarTitle = "formula"
formulaParser.filename = "formulaParser.py"
