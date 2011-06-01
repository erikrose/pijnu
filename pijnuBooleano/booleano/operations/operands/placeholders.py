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
Identifier placeholders.

A placeholder operand is an identifier whose evaluation is not done by Booleano
(i.e., the parse tree is handled directly). As a consequence, the Booleano
parser won't verify its existence.

"""
from booleano.operations import OPERATIONS
from booleano.operations.operands import Operand
from booleano.exc import BadCallError, InvalidOperationError

__all__ = ("VariablePlaceholder", "FunctionPlaceholder")


class PlaceholderOperand(Operand):
    """
    Base class for placeholder operands.
    
    Initially, placeholder operands support all the operations.
    
    .. attribute:: name
    
        The name of the object represented by the placeholder.
    
    """
    
    operations = OPERATIONS
    
    def __init__(self, name):
        """
        Name this placeholder operand as ``name``.
        
        :param name: The name for this placeholder.
        :type name: basestring
        
        """
        self.name = name.lower()
    
    def check_equivalence(self, node):
        """
        Check that placeholder ``node`` is equivalent to this one.
        
        :raises AssertionError: If ``node`` is not a placeholder or if it's
            a placeholder but its name is not equal to current one's.
        
        """
        super(PlaceholderOperand, self).check_equivalence(node)
        assert self.name == node.name, \
               'Placeholders "%s" and "%s" are not equivalent'
    
    def no_evaluation(self, *args, **kwargs):
        """
        Raise an InvalidOperationError exception.
        
        This method should be called when trying to perform an evaluation on
        a placeholder.
        
        """
        raise InvalidOperationError("Placeholders cannot be evaluated!")
    
    # All the evaluation-related operation raise an InvalidOperationError
    to_python = get_logical_value = equals = less_than = greater_than = \
    contains = is_subset = no_evaluation


class VariablePlaceholder(PlaceholderOperand):
    """
    Variable placeholder.
    
    .. attribute:: name
        The name of the variable being represented.
    
    """
    
    def __unicode__(self):
        """Return the Unicode representation for this variable placeholder."""
        return "Variable placeholder %s" % self.name
    
    def __repr__(self):
        """Return the representation for this variable placeholder."""
        return '<Variable placeholder "%s">' % self.name.encode("utf-8")


class FunctionPlaceholder(PlaceholderOperand):
    """
    Function placeholder.
    
    .. attribute:: name
        The name of the function being represented.
    
    .. attribute:: arguments
        The operands passed as arguments for this function.
    
    """
    
    def __init__(self, function_name, *arguments):
        """
        Check that all the  ``arguments`` are operands before creating the
        placeholder for the function called ``function_name``.
        
        :param function_name: The name of the function to be represented.
        :type function_name: basestring
        :raises BadCallError: If one of the ``arguments`` is not an
            :class:`Operand`.
        
        """
        for argument in arguments:
            if not isinstance(argument, Operand):
                raise BadCallError(u'Function placeholder "%s" received a '
                                   'non-operand argument: %s' %
                                   (function_name, argument))
        self.arguments = arguments
        super(FunctionPlaceholder, self).__init__(function_name)
    
    def check_equivalence(self, node):
        """
        Check that function placeholder ``node`` is equivalent to the current
        function placeholder.
        
        :raises AssertionError: If ``node`` is not a function placeholder, or
            if it's a function placeholder but represents a different function.
        
        """
        super(FunctionPlaceholder, self).check_equivalence(node)
        assert self.arguments == node.arguments, \
               u'Function placeholders "%s" and "%s" were called with ' \
               'different arguments' % (self, node)
    
    def __unicode__(self):
        """Return the Unicode representation for this function placeholder."""
        args = [unicode(arg) for arg in self.arguments]
        args = ", ".join(args)
        return "Function placeholder %s(%s)" % (self.name, args)
    
    def __repr__(self):
        """Return the representation for this function placeholder."""
        args = [repr(arg) for arg in self.arguments]
        args = ", ".join(args)
        return "<Function placeholder %s(%s)>" % (self.name.encode("utf-8"),
                                                  args)

