"""
Reading the grammar as UTF-8 raises an exception
"""

from pijnu import makeParser
import codecs
fileObj = codecs.open("bug3.pijnu", "r", "utf-8")
grammar = fileObj.read()
make_parser = makeParser(grammar)
parser = make_parser()
print parser.parseTest('1 2 3')
