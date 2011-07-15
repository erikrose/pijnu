from pijnu.tests import ParserTestCase
from pijnu import makeParser


class ToolsetTests(ParserTestCase):
    """Tests for custom transformation functions"""

    def test_custom_toolset(self):
        """Make sure we can use a custom toolset inside the grammar."""
        numbers_transform_grammar = """\
test_custom_toolset_numbers_transform
<toolset>
def to_real(node):
    node.value = float(node.value)
<definition>
    SEP        : ' '                   : drop
    DOT        : '.'
    digit      : [0..9]
    integer    : digit+                : join
    real       : integer DOT integer?  : join
    number     : real / integer        : to_real
    addedNum   : SEP number            : liftNode
    numbers    : number (addedNum)*    : extract
"""
        make_parser = makeParser(numbers_transform_grammar)
        parser = make_parser()
        source = "1 3.141592 5"
        result = "[integer:'1.0'  real:'3.141592'  integer:'5.0']"
        self.assertEquals(unicode(parser.parseTest(source).value), result)

    def test_external_toolset(self):
        """Make sure we can pass a custom toolset from the make_parser call."""
        def to_real(node):
            node.value = float(node.value)

        numbers_transform_grammar = """\
test_external_toolset_numbers_transform
<definition>
    SEP        : ' '                   : drop
    DOT        : '.'
    digit      : [0..9]
    integer    : digit+                : join
    real       : integer DOT integer?  : join
    number     : real / integer        : to_real
    addedNum   : SEP number            : liftNode
    numbers    : number (addedNum)*    : extract
"""
        make_parser = makeParser(numbers_transform_grammar)
        parser = make_parser({'to_real': to_real})
        source = "1 3.141592 5"
        result = "[integer:'1.0'  real:'3.141592'  integer:'5.0']"
        self.assertEquals(unicode(parser.parseTest(source).value), result)
