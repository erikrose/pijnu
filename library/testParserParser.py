""" testParser
<definition>
    w1 : "foo"
    w2 : "bar"
    ch : w1 / w2

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


    ### title: testParser ###
    
    
    
    
    toolset.update(actions)
    
    ###   <definition>
    w1 = Word('foo', expression='"foo"', name='w1')
    w2 = Word('bar', expression='"bar"', name='w2')
    ch = Choice([w1, w2], expression='w1 / w2', name='ch')

    symbols = locals().copy()
    symbols.update(actions)
    parser._recordPatterns(symbols)
    parser._setTopPattern("ch")
    parser.grammarTitle = "testParser"
    parser.filename = "testParserParser.py"

    return parser
