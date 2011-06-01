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
Identifier operands.

"""
from booleano.operations.operands import Operand, _OperandMeta
from booleano.exc import BadOperandError, BadCallError, BadFunctionError

__all__ = ["Variable", "Function"]


class _IdentifierMeta(_OperandMeta):
    """Metaclass for the identifiers."""
    
    def __init__(cls, name, bases, ns):
        """Lower-case the default names for the node."""
        super(_IdentifierMeta, cls).__init__(name, bases, ns)
        if cls.default_global_name:
            cls.default_global_name = cls.default_global_name.lower()
        for (locale, name) in cls.default_names.items():
            cls.default_names[locale] = name.lower()


class Identifier(Operand):
    """
    Base class for identifiers.
    
    """
    
    __metaclass__ = _IdentifierMeta
    
    # Only actual identifiers should be checked.
    bypass_operation_check = True
    
    default_global_name = None
    
    default_names = {}
    
    def __init__(self, global_name=None, **names):
        """
        Create the identifier using ``global_name`` as it's default name.
        
        :param global_name: The global name used by this identifier; if not set,
            the :attr:`default_global_name` will be used.
        :type global_name: basestring
        :raises BadOperandError: If the identifier class doesn't set a default
            global name and ``global_name`` is not set either.
        
        Additional keyword arguments represent the other names this identifier
        can take in different languages.
        
        .. note::
            ``global_name`` does *not* have to be an English/ASCII string.
        
        """
        if global_name:
            self.global_name = global_name.lower()
        elif self.default_global_name:
            self.global_name = self.default_global_name
        else:
            raise BadOperandError("%s doesn't have a default global name; set "
                                  "one explicitly" % self.__class__.__name__)
        self.names = self.default_names.copy()
        # Convert the ``names`` to lower-case, before updating the resulting
        # names:
        for (locale, name) in names.items():
            names[locale] = name.lower()
        self.names.update(names)
    
    def check_equivalence(self, node):
        """
        Make sure identifier ``node`` and this identifier are equivalent.
        
        :param node: The other identifier which may be equivalent to this one.
        :type node: Identifier
        :raises AssertionError: If the nodes don't share the same class or
            don't share the same global and localized names.
        
        """
        super(Identifier, self).check_equivalence(node)
        assert node.global_name == self.global_name, \
               u'Identifiers %s and %s have different global names' % \
               (self, node)
        assert node.names == self.names, \
               u'Identifiers %s and %s have different translations' % \
               (self, node)


class Variable(Identifier):
    """
    Developer-defined variable.
    
    """
    
    # Only actual variables should be checked.
    bypass_operation_check = True
    
    def __unicode__(self):
        """Return the Unicode representation of this variable."""
        return "Variable %s" % self.global_name
    
    def __repr__(self):
        """Represent this variable, including its translations."""
        names = ['%s="%s"' % (locale, name.encode("utf-8")) for (locale, name)
                 in self.names.items()]
        names.insert(0, '"%s"' % self.global_name.encode("utf-8"))
        names = " ".join(names)
        return "<Variable %s>" % names


class _FunctionMeta(_IdentifierMeta):
    """
    Pre-process user-defined functions right after they've been defined.
    
    """
    
    def __init__(cls, name, bases, ns):
        """
        Calculate the arity of the function and create an utility variable
        which will contain all the valid arguments.
        
        Also checks that there are no duplicate arguments and that each argument
        is an operand.
        
        """
        # A few short-cuts:
        req_args = ns.get("required_arguments", cls.required_arguments)
        opt_args = ns.get("optional_arguments", cls.optional_arguments)
        rargs_set = set(req_args)
        oargs_set = set(opt_args.keys())
        # Checking that are no duplicate entries:
        if len(rargs_set) != len(req_args) or rargs_set & oargs_set:
            raise BadFunctionError('Function "%s" has duplicate arguments'
                                   % name)
        # Checking that the default values for the optional arguments are all
        # operands:
        for (key, value) in opt_args.items():
            if not isinstance(value, Operand):
                raise BadFunctionError('Default value for argument "%s" in '
                                       'function %s is not an operand' %
                                       (key, name))
        # Merging all the arguments into a single list for convenience:
        cls.all_args = tuple(rargs_set | oargs_set)
        # Finding the arity:
        cls.arity = len(cls.all_args)
        # Calling the parent constructor:
        super(_FunctionMeta, cls).__init__(name, bases, ns)


class Function(Identifier):
    """
    Base class for developer-defined, n-ary functions.
    
    Subclasses must override :meth:`check_arguments` to verify the validity of
    the arguments, or to do nothing if it's not necessary.
    
    .. attribute:: required_arguments = ()
    
        The names of the required arguments.
        
        For example, if you have a binary function whose required arguments
        are ``"name"`` and ``"address"``, your function should be defined as::
        
            class MyFunction(Function):
                
                required_arguments = ("name", "address")
                
                # (...)
    
    .. attribute:: optional_arguments = {}
    
        The optional arguments along with their default values.
        
        This is a dictionary whose keys are the argument names and the items
        are their respective default values.
        
        For example, if you have a binary function whose arguments are both
        optional (``"name"`` and ``"address"``), your function should be 
        defined as::
        
            class MyFunction(Function):
                
                # (...)
                
                optional_arguments = {
                    'name': "Gustavo",
                    'address': "Somewhere in Madrid",
                    }
                
                # (...)
        
        Then when it's called without these arguments, their default values
        will be taken.
    
    .. attribute:: arguments
    
        This is an instance attribute which represents the dictionary for the
        received arguments and their values (or their default values, for those
        optional arguments not set explicitly).
    
    .. attribute:: arity
    
        The arity of the function (i.e., the sum of the amount of the required
        arguments and the amount of optional arguments)
    
    .. attribute:: all_args
    
        The names of all the arguments, required and optional.
    
    """
    
    __metaclass__ = _FunctionMeta
    
    # Only actual functions should be checked.
    bypass_operation_check = True
    
    required_arguments = ()
    
    optional_arguments = {}
    
    def __init__(self, global_name=None, *arguments, **names):
        """
        Store the ``arguments`` and validate them.
        
        :param global_name: The global name for this function; if not set,
            the :attr:`default_global_name` will be used..
        :raises BadCallError: If :meth:`check_arguments` finds that the
            ``arguments`` are invalid, or if few arguments are passed, or
            if too much arguments are passed.
        :raises BadOperandError: If the function class doesn't set a default
            global name and ``global_name`` is not set either.
        
        Additional keyword arguments will be used to find the alternative names
        for this functions in various grammars.
        
        """
        super(Function, self).__init__(global_name, **names)
        # Checking the amount of arguments received:
        argn = len(arguments)
        if argn < len(self.required_arguments):
            raise BadCallError("Too few arguments")
        if argn > self.arity:
            raise BadCallError("Too many arguments")
        # Checking that all the arguments are operands:
        for argument in arguments:
            if not isinstance(argument, Operand):
                raise BadCallError('Argument "%s" is not an operand' %
                                   argument)
        # Storing their values:
        self.arguments = self.optional_arguments.copy()
        for arg_pos in range(len(arguments)):
            arg_name = self.all_args[arg_pos]
            self.arguments[arg_name] = arguments[arg_pos]
        # Finally, check that all the parameters are correct:
        self.check_arguments()
    
    def check_arguments(self):
        """
        Check if all the arguments are correct.
        
        :raises BadCallError: If at least one of the arguments are incorrect.
        
        **This method must be overridden in subclasses**.
        
        The arguments dictionary will be available in the :attr:`arguments`
        attribute. If any of them is wrong, this method must raise a
        :class:`BadCallError` exception.
        
        """
        raise NotImplementedError("Functions must validate the arguments")
    
    def check_equivalence(self, node):
        """
        Make sure function ``node`` and this function are equivalent.
        
        :param node: The other function which may be equivalent to this one.
        :type node: Function
        :raises AssertionError: If ``node`` is not a function or if it's a
            function but doesn't have the same arguments as this one OR doesn't
            have the same names as this one.
        
        """
        super(Function, self).check_equivalence(node)
        assert node.arguments == self.arguments, \
               "Functions %s and %s were called with different arguments" % \
               (node, self)
    
    def __unicode__(self):
        """Return the Unicode representation for this function."""
        args = [u'%s=%s' % (k, v) for (k, v) in self.arguments.items()]
        args = ", ".join(args)
        return "%s(%s)" % (self.global_name, args)
    
    def __repr__(self):
        """Return the representation for this function."""
        args = ['%s=%s' % (k, repr(v)) for (k, v) in self.arguments.items()]
        args = ", ".join(args)
        return "<Function %s(%s)>" % (self.global_name.encode("utf-8"), args)

