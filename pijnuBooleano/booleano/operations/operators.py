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
Built-in operators.

"""

from booleano.operations import OPERATIONS, ParseTreeNode
from booleano.operations.operands import Variable
from booleano.exc import InvalidOperationError

__all__ = ("Truth", "Not", "And", "Or", "Xor", "Equal", "NotEqual", "LessThan",
    "GreaterThan", "LessEqual", "GreaterEqual", "Contains", "IsSubset", )


class Operator(ParseTreeNode):
    """
    Base class for logical operators.
    
    The operands to be used by the operator must be passed in the constructor.
    
    """
    
    def __call__(self, **helpers):
        """
        Evaluate the operation, by passing the ``helpers`` to the inner
        operands/operators.
        
        """
        raise NotImplementedError


class UnaryOperator(Operator):
    """
    Base class for unary logical operators.
    
    """
    
    def __init__(self, operand):
        """
        Check that ``operand`` supports all the required operations before
        storing it.
        
        :param operand: The operand handled by this operator.
        :type operand: :class:`booleano.operations.operands.Operand`
        
        """
        self.operand = operand
    
    def check_equivalence(self, node):
        """
        Make sure unary operator ``node`` and this unary operator are
        equivalent.
        
        :param node: The other operator which may be equivalent to this one.
        :type node: UnaryOperator
        :raises AssertionError: If ``node`` is not a unary operator or if it's
            an unary operator but doesn't have the same operand as this one.
        
        """
        super(UnaryOperator, self).check_equivalence(node)
        assert node.operand == self.operand, \
               'Operands of unary operations %s and %s are not equivalent' % \
               (node, self)
    
    def __unicode__(self):
        """
        Return the Unicode representation for this operator and its operand.
        
        """
        operand = unicode(self.operand)
        return u"%s(%s)" % (self.__class__.__name__, operand)
    
    def __repr__(self):
        """Return the representation for this operator and its operand."""
        operand = repr(self.operand)
        return "<%s %s>" % (self.__class__.__name__, operand)


class BinaryOperator(Operator):
    """
    Base class for binary logical operators.
    
    In binary operations, the two operands are marked as "master" or "slave".
    The binary operator will make the *master operand* perform the requested
    operation using the Python value of the *slave operand*. This is found by
    the :meth:`organize_operands` method, which can be overridden.
    
    .. attribute:: master_operand
    
        The instance attribute that represents the master operand.
    
    .. attribute:: slave_operand
    
        The instance attribute that represents the slave operand.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        Instantiate this operator, finding the master operand among
        ``left_operand`` and ``right_operand``.
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.operands.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.operands.Operand`
        
        """
        master, slave = self.organize_operands(left_operand, right_operand)
        self.master_operand = master
        self.slave_operand = slave
    
    def organize_operands(self, left_operand, right_operand):
        """
        Find the master and slave operands among the ``left_operand`` and 
        ``right_operand`` operands.
        
        :param left_operand: The left-hand operand handled by this operator.
        :type left_operand: :class:`booleano.operations.operands.Operand`
        :param right_operand: The right-hand operand handled by this operator.
        :type right_operand: :class:`booleano.operations.operands.Operand`
        :return: A pair where the first item is the master operand and the
            second one is the slave.
        :rtype: tuple
        
        In practice, they are only distinguished when one of the operands is a
        variable and the other is a constant. In such situations, the variable
        becomes the master operand and the constant becomes the slave operand.
        
        When both operands are constant or both are variable, the left-hand 
        operand becomes the master and the right-hand operand becomes the slave.
        
        """
        l_var = isinstance(left_operand, Variable)
        r_var = isinstance(right_operand, Variable)
        
        if l_var == r_var or l_var:
            # Both operands are variable/constant, OR the left-hand operand is 
            # a variable and the right-hand operand is a constant.
            return (left_operand, right_operand)
        
        # The right-hand operand is the variable and the left-hand operand the
        # constant:
        return (right_operand, left_operand)
    
    def check_equivalence(self, node):
        """
        Make sure binary operator ``node`` and this binary operator are
        equivalent.
        
        :param node: The other operator which may be equivalent to this one.
        :type node: BinaryOperator
        :raises AssertionError: If ``node`` is not a binary operator or if it's
            an binary operator but doesn't have the same operands as this one.
        
        """
        super(BinaryOperator, self).check_equivalence(node)
        same_operands = (
            (node.master_operand == self.master_operand and
             node.slave_operand == self.slave_operand)
            or
            (node.master_operand == self.slave_operand and
             self.master_operand == node.slave_operand)
        )
        assert same_operands, \
               'Operands of binary operations %s and %s are not equivalent' % \
               (node, self)
    
    def __unicode__(self):
        """
        Return the Unicode representation for this binary operator, including
        its operands.
        
        If one of the operands is wrapped around a truth operation, such a 
        truth operation will be ignored in the representation.
        
        """
        if isinstance(self.master_operand, Truth):
            master_operand = self.master_operand.operand
        else:
            master_operand = self.master_operand
            
        if isinstance(self.slave_operand, Truth):
            slave_operand = self.slave_operand.operand
        else:
            slave_operand = self.slave_operand
        
        return u"%s(%s, %s)" % (self.__class__.__name__, master_operand,
                                slave_operand)
    
    def __repr__(self):
        """
        Return the representation for this binary operator, including its
        operands.
        
        If one of the operands is wrapped around a truth operation, such a 
        truth operation will be ignored in the representation.
        
        """
        if isinstance(self.master_operand, Truth):
            master_operand = self.master_operand.operand
        else:
            master_operand = self.master_operand
            
        if isinstance(self.slave_operand, Truth):
            slave_operand = self.slave_operand.operand
        else:
            slave_operand = self.slave_operand
        
        return "<%s %s %s>" % (self.__class__.__name__, repr(master_operand),
                               repr(slave_operand))


#{ Unary operators


class Truth(UnaryOperator):
    """
    The truth function.
    
    This is just a wrapper around the ``get_logical_value`` method of the 
    operand, useful for other operators to check the logical value of one
    operand.
    
    In other words, this enables us to use an operand as a boolean expression.
    
    """
    
    def __init__(self, operand):
        """
        Check that ``operand`` supports boolean operations before storing it.
        
        :param operand: The operand in question.
        :type operand: :class:`booleano.operations.operands.Operand`
        :raises InvalidOperationError: If the ``operand`` doesn't support
            boolean operations.
        
        """
#~         if not isinstance(operand, bool):
#~             operand.check_operation("boolean")
        operand.check_operation("boolean")
        super(Truth, self).__init__(operand)
    
    def __call__(self, **helpers):
        """Return the logical value of the operand."""
#~         if isinstance(self.operand, bool):
#~             return self.operand
        return self.operand.get_logical_value(**helpers)
    
    @classmethod
    def convert(cls, operand):
        """
        Turn ``operand`` into a truth operator, unless it's already an operator.
        
        :param operand: The operand to be converted.
        :type operand: Operand or Operator
        :return: The ``operand`` turned into a truth operator if it was an
            actual operand; otherwise it'd be returned as is.
        :rtype: Operator
        
        """
        if not isinstance(operand, Operator):
            return cls(operand)
        return operand


class Not(UnaryOperator):
    """
    The logical negation (``~``).
    
    Negate the boolean representation of an operand.
    
    """
    
    def __init__(self, operand):
        """Turn ``operand`` into a truth operator before storing it."""
        operand = Truth.convert(operand)
        super(Not, self).__init__(operand)
    
    def __call__(self, **helpers):
        """Return the negate of the truth value for the operand."""
        return not self.operand(**helpers)
    
    def __unicode__(self):
        """
        Return the Unicode representation for this operator and its operand,
        removing the Truth function if present.
        
        """
        if isinstance(self.operand, Truth):
            operand = unicode(self.operand.operand)
        else:
            operand = unicode(self.operand)
        return u"%s(%s)" % (self.__class__.__name__, operand)
    
    def __repr__(self):
        """
        Return the representation for this operator and its operand,
        removing the Truth function if present.
        
        """
        if isinstance(self.operand, Truth):
            operand = repr(self.operand.operand)
        else:
            operand = repr(self.operand)
        return "<%s %s>" % (self.__class__.__name__, operand)


#{ Binary operators


class _ConnectiveOperator(BinaryOperator):
    """
    Logic connective to turn the left-hand and right-hand operands into
    boolean operations, so we can manipulate their truth value easily.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        Turn the operands into truth operators so we can manipulate their
        logic value easily and then store them.
        
        """
        left_operand = Truth.convert(left_operand)
        right_operand = Truth.convert(right_operand)
        super(_ConnectiveOperator, self).__init__(left_operand, right_operand)


class And(_ConnectiveOperator):
    """
    The logical conjunction (``AND``).
    
    Connective that checks if two operations evaluate to ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations. If they are actual operands, they'll be wrapped around an
    boolean operation (see :class:`Truth`) so that they can be evaluated
    as an operation.
    
    """
    
    def __call__(self, **helpers):
        """Check if both operands evaluate to ``True``"""
        return self.master_operand(**helpers) and self.slave_operand(**helpers)


class Or(_ConnectiveOperator):
    """
    The logical inclusive disjunction (``OR``).
    
    Connective that check if at least one, out of two operations, evaluate to
    ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations. If they are actual operands, they'll be wrapped around an
    boolean operation (see :class:`Truth`) so that they can be evaluated
    as an operation.
    
    """
    
    def __call__(self, **helpers):
        """Check if at least one of the operands evaluate to ``True``"""
        return self.master_operand(**helpers) or self.slave_operand(**helpers)


class Xor(_ConnectiveOperator):
    """
    The logical exclusive disjunction (``XOR``).
    
    Connective that checks if only one, out of two operations, evaluate to
    ``True``.
    
    With this binary operator, the operands can be actual operands or
    operations. If they are actual operands, they'll be wrapped around an
    boolean operation (see :class:`Truth`) so that they can be evaluated
    as an operation.
    
    """
    
    def __call__(self, **helpers):
        """Check that only one of the operands evaluate to ``True``"""
        return self.master_operand(**helpers) ^ self.slave_operand(**helpers)


class Equal(BinaryOperator):
    """
    The equality operator (``==``).
    
    Checks that two operands are equivalent.
    
    For example: ``3 == 3``.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """Check that the master operand supports equality operations."""
        super(Equal, self).__init__(left_operand, right_operand)
        self.master_operand.check_operation("equality")
    
    def __call__(self, **helpers):
        value = self.slave_operand.to_python(**helpers)
        return self.master_operand.equals(value, **helpers)


# (x <> y) <=> ~(x == y)
class NotEqual(Equal):
    """
    The "not equal to" operator (``!=``).
    
    Checks that two operands are not equivalent.
    
    For example: ``3 != 2``.
    
    """
    
    def __call__(self, **helpers):
        return not super(NotEqual, self).__call__(**helpers)


class _InequalityOperator(BinaryOperator):
    """
    Handle inequalities (``<``, ``>``) and switch the operation if the operands
    are rearranged.
    
    """
    
    def __init__(self, left_operand, right_operand, comparison):
        """
        Switch the ``comparison`` if the operands are rearranged.
        
        :param left_operand: The original left-hand operand in the inequality.
        :param right_operand: The original right-hand operand in the
            inequality.
        :param comparison: The symbol for the particular inequality (i.e.,
            "<" or ">").
        :raises InvalidOperationError: If the master operand doesn't support
            inequalities.
        
        If the operands are rearranged by :meth:`organize_operands`, then
        the operation must be switched (e.g., from "<" to ">").
        
        This will also "compile" the comparison operation; otherwise, it'd have
        to be calculated on a per evaluation basis.
        
        """
        super(_InequalityOperator, self).__init__(left_operand, right_operand)
        
        self.master_operand.check_operation("inequality")
        
        if left_operand != self.master_operand:
            # The operands have been rearranged! Let's invert the comparison:
            if comparison == "<":
                comparison = ">"
            else:
                comparison = "<"
        
        # "Compiling" the comparison:
        if comparison == ">":
            self.comparison = self._greater_than
        else:
            self.comparison = self._less_than
    
    def __call__(self, **helpers):
        return self.comparison(**helpers)
    
    def _greater_than(self, **helpers):
        """Check if the master operand is greater than the slave"""
        value = self.slave_operand.to_python(**helpers)
        return self.master_operand.greater_than(value, **helpers)
    
    def _less_than(self, **helpers):
        """Check if the master operand is less than the slave"""
        value = self.slave_operand.to_python(**helpers)
        return self.master_operand.less_than(value, **helpers)


class LessThan(_InequalityOperator):
    """
    The "less than" operator (``<``).
    
    For example: ``2 < 3``.
    
    """
    
    def __init__(self, left_operand, right_operand):
        super(LessThan, self).__init__(left_operand, right_operand, "<")


class GreaterThan(_InequalityOperator):
    """
    The "greater than" operator (``>``).
    
    For example: ``3 > 2``.
    
    """
    
    def __init__(self, left_operand, right_operand):
        super(GreaterThan, self).__init__(left_operand, right_operand,
                                                  ">")


# (x <= y) <=> ~(x > y)
class LessEqual(GreaterThan):
    """
    The "less than or equal to" operator (``<=``).
    
    For example: ``2 <= 3``.
    
    """
    
    def __call__(self, **helpers):
        return not super(LessEqual, self).__call__(**helpers)


# (x >= y) <=> ~(x < y)
class GreaterEqual(LessThan):
    """
    The "greater than or equal to" operator (``>=``).
    
    For example: ``2 >= 2``.
    
    """
    
    def __call__(self, **helpers):
        return not super(GreaterEqual, self).__call__(**helpers)


class _SetOperator(BinaryOperator):
    """
    Base class for set-related operators.
    
    """
    
    def __init__(self, left_operand, right_operand):
        """
        Check if the set (right-hand operand) supports memberships operations.
        
        """
        super(_SetOperator, self).__init__(left_operand, right_operand)
        self.master_operand.check_operation("membership")
    
    def organize_operands(self, left_operand, right_operand):
        """Set the set (right-hand operand) as the master operand."""
        return (right_operand, left_operand)


class Contains(_SetOperator):
    """
    The "belongs to" operator (``∈``).
    
    For example: ``"valencia" ∈ {"caracas", "maracay", "valencia"}``.
    
    """
    
    def __call__(self, **helpers):
        value = self.slave_operand.to_python(**helpers)
        return self.master_operand.contains(value, **helpers)


class IsSubset(_SetOperator):
    """
    The "is a subset of" operator (``⊂``).
    
    For example: ``{"valencia", "aragua"} ⊂ {"caracas", "aragua", "valencia"}``.
    
    """
    
    def __call__(self, **helpers):
        value = self.slave_operand.to_python(**helpers)
        return self.master_operand.is_subset(value, **helpers)


#}
