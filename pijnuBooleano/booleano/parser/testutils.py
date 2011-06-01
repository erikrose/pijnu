# -*- coding: utf-8 -*-
#

''' © copyright 2009 Denis Derman
	contact: denis <dot> spir <at> free <dot> fr
	
    This file is part of PIJNU.
	
    PIJNU is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
	
    PIJNU is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
	
    You should have received a copy of the GNU General Public License
    along with PIJNU: see the file called 'GPL'.
    If not, see <http://www.gnu.org/licenses/>.
	'''
# Copyright (c) 2009 by Gustavo Narea <http://gustavonarea.net/>.
#
# This file is part of Booleano <http://code.gustavonarea.net/booleano/>.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, distribute with
# modifications, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# ABOVE COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
# IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name(s) of the above copyright
# holders shall not be used in advertising or otherwise to promote the sale,
# use or other dealings in this Software without prior written authorization.
"""
Utilities to test Booleano grammars.

"""
from nose.tools import eq_, ok_, raises
from pyparsing import ParseException

__all__ = ["BaseParseTest"]


class BaseParseTest(object):
    """
    The base test case for the parser of a grammar.
    
    Subclasses must define all the following attributes for the test case to
    work.
    
    .. attribute:: grammar
    
        An instance of the grammar to be tested.
    
    .. attribute:: expressions
    
        A dictionary with all the valid expressions recognized by the grammar,
        where each key is the expression itself and its item is the mock
        representation of the operation.
    
    """
    
    def test_infinitely_recursive_constructs(self):
        """There must not exist infinitely recursive constructs."""
        self.grammar.define_string().validate()
        self.grammar.define_number().validate()
        self.grammar.define_variable().validate()
        # Validating all the operands together, including sets:
        self.grammar.define_operand().validate()
        # Finally, validate the whole grammar:
        self.grammar.grammar.validate()
    
    def test_valid_expressions(self):
        for expression, expected_node in self.expressions.items():
            yield (check_expression, self.grammar, expression,
                   expected_node)
    
    def test_operands_alone(self):
        operand_parser = self.grammar.define_operand().parseString
        for expression, expected_node in self.valid_operands.items():
            yield (check_operand, operand_parser, expression,
                   expected_node)
        for expression in self.invalid_operands:
            yield (check_invalid_operand, operand_parser, expression)


def check_expression(parser, expression, expected_node):
    node = parser(expression)
    expected_node.check_equivalence(node)


def check_operand(parser, expression, expected_node):
    node = parser(expression, parseAll=True)
    eq_(1, len(node))
    expected_node.check_equivalence(node[0])


@raises(ParseException)
def check_invalid_operand(parser, expression):
    parser(expression, parseAll=True)

