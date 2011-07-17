"""
Calling a repetition inside another produces an infinite loop.
"""

from pijnu import makeParser
numbers_transform_grammar = """
test_custom_toolset_numbers_transform
<toolset>
def to_real(node):
    node.value = float(node.value)
<definition>
    SEP        : ' '                   : drop
    DOT        : '.'
    digit      : [0..9]
    integer    : digit*                : join
    integer2   : integer*
    real       : integer DOT integer?  : join
    number     : real / integer2       : to_real
    addedNum   : SEP number            : liftNode
    numbers    : number (addedNum)*    : extract
"""
make_parser = makeParser(numbers_transform_grammar)
parser = make_parser()
print parser.parseTest('1 2 3')
