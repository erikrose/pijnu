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
Constant operands.

"""
from booleano.operations.operands import Operand
from booleano.exc import InvalidOperationError

__all__ = ["String", "Number", "Set"]


class Constant(Operand):
    """
    Base class for constant operands.
    
    The only operation that is common to all the constants is equality (see
    :meth:`equals`).
    
    Constants don't rely on helpers -- they are constant!
    
    .. warning::
        This class is available as the base for the built-in :class:`String`,
        :class:`Number` and :class:`Set` classes. User-defined constants aren't
        supported; use :class:`Variable` instead.
    
    """
    
    operations = set(['equality'])
    
    def __init__(self, constant_value):
        """
        Initialize this constant as ``constant_value``.
        
        """
        self.constant_value = constant_value
    
    def to_python(self, **helpers):
        """
        Return the value represented by this constant.
        
        """
        return self.constant_value
    
    def equals(self, value, **helpers):
        """
        Check if this constant equals ``value``.
        
        """
        return self.constant_value == value
    
    def check_equivalence(self, node):
        """
        Make sure constant ``node`` and this constant are equivalent.
        
        :param node: The other constant which may be equivalent to this one.
        :type node: Constant
        :raises AssertionError: If the constants are of different types or
            represent different values.
        
        """
        super(Constant, self).check_equivalence(node)
        assert node.constant_value == self.constant_value, \
               u'Constants %s and %s represent different values' % (self,
                                                                    node)


class String(Constant):
    u"""
    Constant string.
    
    These constants only support equality operations.
    
    .. note:: **Membership operations aren't supported**
    
        Although both sets and strings are item collections, the former is 
        unordered and the later is ordered. If they were supported, there would
        some ambiguities to sort out, because users would expect the following
        operation results::
        
        - ``"ao" ⊂ "hola"`` is false: If strings were also sets, then the 
          resulting operation would be ``{"a", "o"} ⊂ {"h", "o", "l", "a"}``,
          which is true.
        - ``"la" ∈ "hola"`` is true: If strings were also sets, then the 
          resulting operation would be ``{"l", "a"} ∈ {"h", "o", "l", "a"}``, 
          which would be an *invalid operation* because the first operand must 
          be an item, not a set. But if we make an exception and take the first 
          operand as an item, the resulting operation would be 
          ``"la" ∈ {"h", "o", "l", "a"}``, which is not true.
        
        The solution to the problems above would involve some magic which
        contradicts the definition of a set: Take the second operand as an 
        *ordered collection*. But it'd just cause more trouble, because both
        operations would be equivalent!
        
        Also, there would be other issues to take into account (or not), like
        case-sensitivity.
        
        Therefore, if this functionality is needed, developers should create
        function operators to handle it.
    
    """
    
    def __init__(self, string):
        """Turn ``string`` into a string if it isn't a string yet"""
        string = unicode(string)
        super(String, self).__init__(string)
    
    def equals(self, value, **helpers):
        """Turn ``value`` into a string if it isn't a string yet"""
        value = unicode(value)
        return super(String, self).equals(value, **helpers)
    
    def __unicode__(self):
        """Return the Unicode representation of this constant string."""
        return u'"%s"' % self.constant_value
    
    def __repr__(self):
        """Return the representation for this constant string."""
        return '<String "%s">' % self.constant_value.encode("utf-8")


class Number(Constant):
    """
    Float and integer constants.
    
    These constants support inequality operations; see :meth:`greater_than`
    and :meth:`less_than`.
    
    Internally, this number is treated like a float, even if it was an
    integer initially.
    
    """
    
    operations = Constant.operations | set(['inequality'])
    
    def __init__(self, number):
        """
        Turn ``number`` into a float before instantiating this constant.
        
        """
        number = float(number)
        super(Number, self).__init__(number)
    
    def equals(self, value, **helpers):
        """
        Check if this numeric constant equals ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to 
        support strings.
        
        :raises InvalidOperationError: If ``value`` can't be turned into a
            float.
        
        """
        try:
            value = float(value)
#~         except (ValueError,TypeError):
        except (ValueError):
            raise InvalidOperationError('"%s" is not a number' % value)
        
        return super(Number, self).equals(value, **helpers)
    
    def greater_than(self, value, **helpers):
        """
        Check if this numeric constant is greater than ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value > float(value)
    
    def less_than(self, value, **helpers):
        """
        Check if this numeric constant is less than ``value``.
        
        ``value`` will be turned into a float prior to the comparison, to
        support strings.
        
        """
        return self.constant_value < float(value)
    
    def __unicode__(self):
        """Return the Unicode representation of this constant number."""
        return unicode(self.constant_value)
    
    def __repr__(self):
        """Return the representation for this constant number."""
        return '<Number %s>' % self.constant_value


class Set(Constant):
    """
    Constant sets.
    
    These constants support membership operations; see :meth:`contains` and
    :meth:`is_subset`.
    
    """
    
    operations = Constant.operations | set(["inequality", "membership"])
    
    def __init__(self, *items):
        """
        Check that each item in ``items`` is an operand before setting up this
        set.
        
        :raises InvalidOperationError: If at least one of the ``items`` is not
            an instance of :class:`Operand`.
        
        """
        for item in items:
            if not isinstance(item, Operand):
                raise InvalidOperationError('Item "%s" is not an operand, so '
                                            'it cannot be a member of a set' %
                                            item)
        super(Set, self).__init__(set(items))
#~         super(Set, self).__init__(frozenset(items))
    
    def to_python(self, **helpers):
        """
        Return a set made up of the Python representation of the operands
        contained in this set.
        
        """
        items = set(item.to_python(**helpers) for item in self.constant_value)
#~         items = frozenset(item.to_python(**helpers) for item in self.constant_value)
        return items
    
    def equals(self, value, **helpers):
        """Check if all the items in ``value`` are the same of this set."""
        value = set(value)
#~         try:
#~             value = set(value)
#~ ##~             value = frozenset(value)
#~         except TypeError:
#~             return False
        return value == self.to_python(**helpers)
    
    def less_than(self, value, **helpers):
        """
        Check if this set has less items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        try:
            value = float(value)
            if not value.is_integer():
                raise ValueError
        except ValueError:
            raise InvalidOperationError('To compare the amount of items in a '
                                        'set, the operand "%s" has to be an '
                                        'integer')
        return len(self.constant_value) < value
    
    def greater_than(self, value, **helpers):
        """
        Check if this set has more items than the number represented in 
        ``value``.
        
        :raises InvalidOperationError: If ``value`` is not an integer.
        
        """
        try:
            value = float(value)
            if not value.is_integer():
                raise ValueError
        except ValueError:
            raise InvalidOperationError('To compare the amount of items in a '
                                        'set, the operand "%s" has to be an '
                                        'integer')
        return len(self.constant_value) > value
    
    def contains(self, value, **helpers):
        """
        Check that this constant set contains the ``value`` item.
        
        """
        for item in self.constant_value:
            try:
                if item.equals(value, **helpers):
                    return True
            except InvalidOperationError:
                continue
        return False
    
    def is_subset(self, value, **helpers):
        """
        Check that the ``value`` set is a subset of this constant set.
        
        """
        for item in value:
            if not self.contains(item, **helpers):
                return False
        return True
    
    def check_equivalence(self, node):
        """
        Make sure set ``node`` and this set are equivalent.
        
        :param node: The other set which may be equivalent to this one.
        :type node: Set
        :raises AssertionError: If ``node`` is not a set or it's a set 
            with different elements.
        
        """
        Operand.check_equivalence(self, node)
        
        unmatched_elements = list(self.constant_value)
        assert len(unmatched_elements) == len(node.constant_value), \
               u'Sets %s and %s do not have the same cardinality' % \
               (unmatched_elements, node)
        
        # Checking that each element is represented by a mock operand:
        for element in node.constant_value:
            for key in range(len(unmatched_elements)):
                if unmatched_elements[key] == element:
                    del unmatched_elements[key]
                    break
        
        assert 0 == len(unmatched_elements), \
               u'No match for the following elements: %s' % unmatched_elements
    
    def __unicode__(self):
        """Return the Unicode representation of this constant set."""
        elements = [unicode(element) for element in self.constant_value]
        elements = u", ".join(elements)
        return "{%s}" % elements
    
    def __repr__(self):
        """Return the representation for this constant set."""
        elements = [repr(element) for element in self.constant_value]
        elements = u", ".join(elements)
        if elements:
            elements = " " + elements
        return '<Set%s>' % elements

