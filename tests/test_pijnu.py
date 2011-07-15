from pijnu.tests import ParserTestCase


class ToolsetTests(ParserTestCase):
    """Tests for custom transformation functions"""

    def test_custom_toolset(self):
        """Make sure plugging in a custom quote-parsing postprocessor works."""
        from pijnu import makeParser
        numbersTransformGrammar = """\
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
        make_parser = makeParser(numbersTransformGrammar)
        parser = make_parser()
        source = "1 3.141592 5"
        result = "[integer:'1.0'  real:'3.141592'  integer:'5.0']"
        self.assertEquals(unicode(parser.parseTest(source).value), result)

    def test_external_toolset(self):
        """Make sure plugging in a custom quote-parsing postprocessor works."""
        from pijnu import makeParser
        def to_real(node):
            node.value = float(node.value)

        numbersTransformGrammar = """\
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
        make_parser = makeParser(numbersTransformGrammar)
        parser = make_parser({'to_real': to_real})
        source = "1 3.141592 5"
        result = "[integer:'1.0'  real:'3.141592'  integer:'5.0']"
        self.assertEquals(unicode(parser.parseTest(source).value), result)
