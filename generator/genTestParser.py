""" genTest
<definition>
# constants
	SPACE		: ' '							: drop
	SPACING		: SPACE*						: drop
	DOT			: "."
	MINUS		: "-"
	PLUS		: "+"							: drop
	ADD			: PLUS
	_ADD_		: SPACING ADD SPACING			: drop
	MULT		: "*"
	_MULT_		: SPACING MULT SPACING			: drop
	DIGIT		: [0..9]
	SIGN		: PLUS / MINUS
	SIGN_		: SIGN SPACING
	LPAREN		: "("							: drop
	RPAREN		: ")"							: drop

# operand
	digits		: DIGIT+
	integer		: SIGN_? digits
	real		: integer (DOT digits)?
	number		: real / integer				: join toFloat
	group		: LPAREN operation RPAREN		: liftNode
	operand 	: group / number

# operation
	mult		: operand _MULT_ (mult/operand)	: @ doMult
	addOp		: mult / operand
	add			: addOp _ADD_  (add/addOp)		: @ doAdd
	operation	: add / mult					: @
	foo			: ("a"/"b"){3}
	bar			: [1..9]{3}
	baz			: '1'{3}
	result		: operation / operand			: formatResult

"""

from pijnu.library import *


def make_parser(actions=None):
    """Return a parser.

    The parser's toolset functions are (optionally) augmented (or overridden)
    by a map of additional ones passed in.

    """
    if actions is None:
        actions = {}

    # Start off with the imported pijnu library functions:
    toolset = globals().copy()

    parser = Parser()
    state = parser.state

# a mini test grammar for the generator
    
    ### title: genTest ###
    
    
    
    def toolset_from_grammar():
        """Return a map of toolset functions hard-coded into the grammar."""
    ###   <toolset>
        def doMult(node):
        	(a,b) = node
        	node.value = a.value * b.value
        
        def doAdd(node):
        	(a,b) = node
        	node.value = a.value + b.value
        
        def formatResult(node):
        	node.value = "%.3f" % node.value
    
        return locals().copy()
    
    toolset.update(toolset_from_grammar())
    toolset.update(actions)
    
    ###   <definition>
    # recursive pattern(s)
    operation = Recursive(name='operation')
    add = Recursive(name='add')
    mult = Recursive(name='mult')
    # constants
    SPACE = Char(' ', expression="' '", name='SPACE')(toolset['drop'])
    SPACING = Repetition(SPACE, numMin=False, numMax=False, expression='SPACE*', name='SPACING')(toolset['drop'])
    DOT = Word('.', expression='"."', name='DOT')
    MINUS = Word('-', expression='"-"', name='MINUS')
    PLUS = Word('+', expression='"+"', name='PLUS')(toolset['drop'])
    ADD = Clone(PLUS, expression='PLUS', name='ADD')
    _ADD_ = Sequence([SPACING, ADD, SPACING], expression='SPACING ADD SPACING', name='_ADD_')(toolset['drop'])
    MULT = Word('*', expression='"*"', name='MULT')
    _MULT_ = Sequence([SPACING, MULT, SPACING], expression='SPACING MULT SPACING', name='_MULT_')(toolset['drop'])
    DIGIT = Klass(u'0123456789', expression='[0..9]', name='DIGIT')
    SIGN = Choice([PLUS, MINUS], expression='PLUS / MINUS', name='SIGN')
    SIGN_ = Sequence([SIGN, SPACING], expression='SIGN SPACING', name='SIGN_')
    LPAREN = Word('(', expression='"("', name='LPAREN')(toolset['drop'])
    RPAREN = Word(')', expression='")"', name='RPAREN')(toolset['drop'])
    
    # operand
    digits = Repetition(DIGIT, numMin=1, numMax=False, expression='DIGIT+', name='digits')
    integer = Sequence([Option(SIGN_, expression='SIGN_?'), digits], expression='SIGN_? digits', name='integer')
    real = Sequence([integer, Option(Sequence([DOT, digits], expression='DOT digits'), expression='(DOT digits)?')], expression='integer (DOT digits)?', name='real')
    number = Choice([real, integer], expression='real / integer', name='number')(toolset['join'], toolset['toFloat'])
    group = Sequence([LPAREN, operation, RPAREN], expression='LPAREN operation RPAREN', name='group')(toolset['liftNode'])
    operand = Choice([group, number], expression='group / number', name='operand')
    
    # operation
    mult **= Sequence([operand, _MULT_, Choice([mult, operand], expression='mult/operand')], expression='operand _MULT_ (mult/operand)', name='mult')(toolset['doMult'])
    addOp = Choice([mult, operand], expression='mult / operand', name='addOp')
    add **= Sequence([addOp, _ADD_, Choice([add, addOp], expression='add/addOp')], expression='addOp _ADD_  (add/addOp)', name='add')(toolset['doAdd'])
    operation **= Choice([add, mult], expression='add / mult', name='operation')
    foo = Repetition(Choice([Word('a', expression='"a"'), Word('b', expression='"b"')], expression='"a"/"b"'), numMin=3, numMax=3, expression='("a"/"b"){3}', name='foo')
    bar = Repetition(Klass(u'123456789', expression='[1..9]'), numMin=3, numMax=3, expression='[1..9]{3}', name='bar')
    baz = Repetition(Char('1', expression="'1'"), numMin=3, numMax=3, expression="'1'{3}", name='baz')
    result = Choice([operation, operand], expression='operation / operand', name='result')(toolset['formatResult'])

    symbols = locals().copy()
    symbols.update(actions)
    parser._recordPatterns(symbols)
    parser._setTopPattern("result")
    parser.grammarTitle = "genTest"
    parser.filename = "genTestParser.py"

    return parser
