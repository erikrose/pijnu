# coding:utf8

''' A mini test for the generator
	
	uses genTestParser.py, generated from genTest.pijnu
	'''

from sys import exit as end

# get parser
from pijnu.generator import makeParser
grammar = file("genTest.pijnu").read()

#~ grammar = """
#~ genTest
#~ <toolset>
#~ pass
#~ <definition>
#~ X	: 'x'
#~ XX	: X XXX			: join
#~ XXX	: XX / X		: @
#~ """
#~ parser = makeParser(grammar)
#~ source = r"""x xxx xxxxx"""
#~ parser.test(source,"findAll")
#~ end()

parser = makeParser(grammar)

# test it
sources = """\
1
- 1.1
1.1 * -2
-3 + +4.4
-3 ++4.4
3 *-4.4
9*8*7*6*5
1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1*1
9+8+7+6+5
3*(2+1)
1*4 + 3*2
""".splitlines()
parser.testSuiteDict(sources)

print parser.digits
print parser.foo
print parser.bar
print parser.baz
print repr(parser.foo)
print repr(parser.bar)
print repr(parser.baz)
print parser.foo.pattern
print parser.bar.klass
print parser.baz.klass
