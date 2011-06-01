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
Converters for Booleano parse tree structures.

"""
from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, Contains, IsSubset,
    String, Number, Set, VariablePlaceholder, FunctionPlaceholder)
from booleano.operations.operators import UnaryOperator
from booleano.operations.operands.constants import Constant
from booleano.exc import ConversionError

__all__ = ("BaseConverter", )


class BaseConverter(object):
    """The base class for converters."""
    
    converters = {
        # Operation converters:
        Truth: "convert_truth",
        Not: "convert_not",
        And: "convert_and",
        Or: "convert_or",
        Xor: "convert_xor",
        Equal: "convert_equal",
        NotEqual: "convert_not_equal",
        LessThan: "convert_less_than",
        GreaterThan: "convert_greater_than",
        LessEqual: "convert_less_equal",
        GreaterEqual: "convert_greater_equal",
        Contains: "convert_contains",
        IsSubset: "convert_is_subset",
        # Operand converters:
        String: "convert_string",
        Number: "convert_number",
        Set: "convert_set",
        VariablePlaceholder: "convert_variable",
        FunctionPlaceholder: "convert_function",
    }
    
    def __call__(self, parse_tree):
        """
        Convert ``parse_tree``.
        
        :param parse_tree: The parse tree to be converted.
        :type parse_tree: ParseTreeNode
        :return: The parse tree converted.
        :raises ConversionError: If the type of ``parse_tree`` is unknown.
        
        If ``node`` is a branch, its children will be converted first.
        
        """
        parse_tree_type = parse_tree.__class__
        if parse_tree_type not in self.converters:
            raise ConversionError("Unknown tree type: %s" % parse_tree_type)
        return self.convert(parse_tree)
    
    def convert(self, node):
        """
        Convert ``node``.
        
        :param node: The node to be converted.
        :type node: ParseTreeNode
        :return: The node converted.
        
        If ``node`` is a branch, its children will be converted first.
        
        """
        convert = getattr(self, self.converters[node.__class__])
        
        if node.is_leaf():
            if isinstance(node, VariablePlaceholder):
                return convert(node.name)
            # It's a string or a number
            return convert(node.constant_value)
        
        if isinstance(node, Set):
            elements = [self.convert(element) for element
                        in node.constant_value]
            return convert(*elements)
        
        if isinstance(node, FunctionPlaceholder):
            arguments = [self.convert(arg) for arg in node.arguments]
            return convert(node.name, *arguments)
        
        # At this point, node must be an operator.
        
        if isinstance(node, UnaryOperator):
            operand = self.convert(node.operand)
            return convert(operand)
        
        # It's a binary operator!
        master_operand = self.convert(node.master_operand)
        slave_operand = self.convert(node.slave_operand)
        return convert(master_operand, slave_operand)
    
    #{ Operation converters
    
    def convert_truth(self, operand):
        """
        Convert truth function whose argument is ``operand``.
        
        :param operand: The argument already converted.
        
        """
        raise NotImplementedError
    
    def convert_not(self, operand):
        """
        Convert negation function whose argument is ``operand``.
        
        :param operand: The argument already converted.
        
        """
        raise NotImplementedError
    
    def convert_and(self, master_operand, slave_operand):
        """
        Convert AND connective whose left-hand operand is ``master_operand``
        and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_or(self, master_operand, slave_operand):
        """
        Convert OR connective whose left-hand operand is ``master_operand``
        and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_xor(self, master_operand, slave_operand):
        """
        Convert XOR connective whose left-hand operand is ``master_operand``
        and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_equal(self, master_operand, slave_operand):
        """
        Convert equality operation whose left-hand operand is ``master_operand``
        and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_not_equal(self, master_operand, slave_operand):
        """
        Convert "not equal to" operation whose left-hand operand is 
        ``master_operand`` and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_less_than(self, master_operand, slave_operand):
        """
        Convert "less than" operation whose left-hand operand is 
        ``master_operand`` and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_greater_than(self, master_operand, slave_operand):
        """
        Convert "greater than" operation whose left-hand operand is 
        ``master_operand`` and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_less_equal(self, master_operand, slave_operand):
        """
        Convert "less than or equal to" operation whose left-hand operand is 
        ``master_operand`` and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_greater_equal(self, master_operand, slave_operand):
        """
        Convert "greater than or equal to" operation whose left-hand operand is 
        ``master_operand`` and right-hand operand is ``slave_operand``.
        
        :param master_operand: The left-hand operand, already converted.
        :param slave_operand: The right-hand operand, already converted.
        
        """
        raise NotImplementedError
    
    def convert_contains(self, master_operand, slave_operand):
        """
        Convert "belongs to" operation where the set is 
        ``master_operand`` and the element is ``slave_operand``.
        
        :param master_operand: The set already converted.
        :param slave_operand: The element already converted.
        
        """
        raise NotImplementedError
    
    def convert_is_subset(self, master_operand, slave_operand):
        """
        Convert "is subset of" operation where the superset is 
        ``master_operand`` and the subset is ``slave_operand``.
        
        :param master_operand: The superset already converted.
        :param slave_operand: The subset already converted.
        
        """
        raise NotImplementedError
    
    #{ Operand converters
    
    def convert_string(self, operand):
        """Convert the constant string ``operand``."""
        raise NotImplementedError
    
    def convert_number(self, operand):
        """Convert the constant number ``operand``."""
        raise NotImplementedError
    
    def convert_set(self, *operands):
        """Convert the set ``operand``."""
        raise NotImplementedError
    
    def convert_variable(self, name):
        """
        Convert the variable called ``name``.
        
        :param name: The name of the variable.
        :type name: basestring
        
        """
        raise NotImplementedError
    
    def convert_function(self, name, *arguments):
        """
        Convert the function call to ``name`` using the additional positional
        arguments as the arguments of the call.
        
        :param name: The name of the function being called.
        :type name: basestring
        
        The arguments will be received converted.
        
        """
        raise NotImplementedError
    
    #}
