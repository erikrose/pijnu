"""
Cloning a Choice pattern raises a TypeError exception.

It might also happen with other types of patterns.
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
    integer    : digit+                : join
    integer2   : integer
    real       : integer DOT integer?  : join
    number     : real / integer        : to_real
    number2    : number
    addedNum   : SEP number            : liftNode
    numbers    : number (addedNum)*    : extract
"""
make_parser = makeParser(numbers_transform_grammar)
parser = make_parser()
print parser.parseTest('1 2 3')
