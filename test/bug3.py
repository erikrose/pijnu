# -*- coding: utf8 -*-

"""
Some characters (such as `©`) are not allowed in comments.
"""

from pijnu import makeParser
grammar = file("bug3.pijnu").read()
make_parser = makeParser(grammar)
parser = make_parser()
print parser.parseTest('1 2 3')
