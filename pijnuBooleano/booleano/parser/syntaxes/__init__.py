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
Syntax localizations for the boolean expressions.

This module contains the generic grammar, which uses mathematical symbols only
and no words.

"""
import re

from pyparsing import (Suppress, CaselessLiteral, Word, quotedString, alphas,
    nums, operatorPrecedence, opAssoc, Forward, ParseException, removeQuotes,
    Optional, OneOrMore, Combine, StringStart, StringEnd, ZeroOrMore, Group,
    Regex, Literal, delimitedList)

from booleano.operations import (Truth, Not, And, Or, Xor, Equal, NotEqual,
    LessThan, GreaterThan, LessEqual, GreaterEqual, Contains, IsSubset,
    String, Number, Set, Variable, Function)


__all__ = ["GenericGrammar"]


class _GrammarMeta(type):
    """
    Complete a grammar right after the basic settings have been defined.
    
    This is the meta class for the grammars, which will build each grammar
    once the individual tokens are defined.
    
    """
    
    def __init__(cls, name, bases, ns):
        tokens = cls.__dict__.copy()
        tokens.update(ns)
        
        grp_start = Suppress(tokens['T_GROUP_START'])
        grp_end = Suppress(tokens['T_GROUP_END'])
        
        # Making the relational operations:
        eq = CaselessLiteral(tokens['T_EQ'])
        ne = CaselessLiteral(tokens['T_NE'])
        lt = CaselessLiteral(tokens['T_LT'])
        gt = CaselessLiteral(tokens['T_GT'])
        le = CaselessLiteral(tokens['T_LE'])
        ge = CaselessLiteral(tokens['T_GE'])
        relationals = eq | ne | lt | gt | le | ge
        cls.__operations__ = {
            tokens['T_EQ']: Equal,
            tokens['T_NE']: NotEqual,
            tokens['T_LT']: LessThan,
            tokens['T_GT']: GreaterThan,
            tokens['T_LE']: LessEqual,
            tokens['T_GE']: GreaterEqual,
        }
        
        # Making the logical connectives:
        not_ = CaselessLiteral(tokens['T_NOT'])
        and_ = CaselessLiteral(tokens['T_AND'])
        in_or = CaselessLiteral(tokens['T_OR'])
        ex_or = CaselessLiteral(tokens['T_XOR'])
        or_ = in_or | ex_or
        
        operand = cls.define_operand()
        
        grammar = operatorPrecedence(
            operand,
            [
                (relationals, 2, opAssoc.LEFT, cls.make_relational),
                #(not_, 1, opAssoc.RIGHT),
                (and_, 2, opAssoc.LEFT),
                (or_, 2, opAssoc.LEFT),
            ]
        )
        
        cls.grammar = StringStart() + grammar + StringEnd()


class GenericGrammar(object):
    
    __metaclass__ = _GrammarMeta
    
    locale = "xx"
    
    #{ Default tokens/operators.
    
    # Some logical connectives:
    T_NOT = "~"
    T_AND = "&"
    T_OR = "|"
    T_XOR = "^"
    
    # Relational operators:
    T_EQ = "=="
    T_NE = "!="
    T_LT = "<"
    T_GT = ">"
    T_LE = "<="
    T_GE = ">="
    
    # Set operators:
    T_IN = u"∈"
    T_CONTAINED = u"⊂"
    T_SET_START = "{"
    T_SET_END = "}"
    T_ELEMENT_SEPARATOR = ","
    
    # Grouping marks:
    T_STRING_START = '"'
    T_STRING_END = '"'
    T_GROUP_START = "("
    T_GROUP_END = ")"
    
    # Signed numbers:
    T_POSITIVE_SIGN = "+"
    T_NEGATIVE_SIGN = "-"
    
    # Miscellaneous tokens:
    T_VARIABLE_SPACING = "_"
    T_DECIMAL_SEPARATOR = "."
    T_THOUSANDS_SEPARATOR = ","
    
    def __init__(self, variables={}, var_containers={}, functions={}):
        self.variables = variables
        self.var_containers = var_containers
        self.functions = functions
    
    def __call__(self, expression):
        """
        Parse ``expression`` and return its parse tree.
        
        """
        node = self.grammar.parseString(expression, parseAll=True)
        return node[0]
    
    #{ Operand generators; used to create the grammar
    
    @classmethod
    def define_operand(cls):
        """
        Return the syntax definition for an operand.
        
        An operand can be a variable, a string, a number or a set. A set
        is made of other operands, including other sets.
        
        **This method shouldn't be overridden**. Instead, override the syntax
        definitions for variables, strings and/or numbers.
        
        If you want to customize the sets, check :meth:`T_SET_START`,
        :meth:`T_SET_END` and :meth:`T_ELEMENT_SEPARATOR`.
        
        """
        operand = Forward()
        
        set_start = Suppress(cls.T_SET_START)
        set_end = Suppress(cls.T_SET_END)
        elements = delimitedList(operand, delim=cls.T_ELEMENT_SEPARATOR)
        set_ = Group(set_start + Optional(elements) + set_end)
        set_.setParseAction(cls.make_set)
        set_.setName("set")
        
        operand << (cls.define_variable() | cls.define_number() | \
                    cls.define_string() | set_)
        
        return operand
    
    @classmethod
    def define_string(cls):
        """
        Return the syntax definition for a string.
        
        **Do not override this method**, it's not necessary: it already
        supports unicode strings. If you want to override the delimiters,
        check :attr:`T_QUOTES`.
        
        """
        string = quotedString.setParseAction(removeQuotes, cls.make_string)
        string.setName("string")
        return string
    
    @classmethod
    def define_number(cls):
        """
        Return the syntax definition for a number in Arabic Numerals.
        
        Override this method to support numeral systems other than Arabic
        Numerals (0-9).
        
        Do not override this method just to change the character used to
        separate thousands and decimals: Use :attr:`T_THOUSANDS_SEPARATOR`
        and :attr:`T_DECIMAL_SEPARATOR`, respectively.
        
        """
        # Defining the basic tokens:
        to_dot = lambda t: "."
        to_plus = lambda t: "+"
        to_minus = lambda t: "-"
        positive_sign = Literal(cls.T_POSITIVE_SIGN).setParseAction(to_plus)
        negative_sign = Literal(cls.T_NEGATIVE_SIGN).setParseAction(to_minus)
        decimal_sep = Literal(cls.T_DECIMAL_SEPARATOR).setParseAction(to_dot)
        thousands_sep = Suppress(cls.T_THOUSANDS_SEPARATOR)
        digits = Word(nums)
        # Building the integers and decimals:
        sign = positive_sign | negative_sign
        thousands = Word(nums, max=3) + \
                    OneOrMore(thousands_sep + Word(nums, exact=3))
        integers = thousands | digits
        decimals = decimal_sep + digits
        number = Combine(Optional(sign) + integers + Optional(decimals))
        number.setParseAction(cls.make_number)
        number.setName("number")
        return number
    
    @classmethod
    def define_variable(cls):
        """
        Return the syntax definition for a variable.
        
        """
        def first_not_a_number(tokens):
            if tokens[0][0].isdigit():
                raise ParseException('Variable "%s" must not start by a '
                                     'number' % tokens[0])
        space_char = re.escape(cls.T_VARIABLE_SPACING)
        variable = Regex("[\w%s]+" % space_char, re.UNICODE)
        variable.setParseAction(first_not_a_number, cls.make_variable)
        variable.setName("variable")
        return variable
    
    #{ Parse actions
    
    @classmethod
    def make_string(cls, tokens):
        """Make a String constant using the token passed."""
        return String(tokens[0])
    
    @classmethod
    def make_number(cls, tokens):
        """Make a Number constant using the token passed."""
        return Number(tokens[0])
    
    @classmethod
    def make_variable(cls, tokens):
        """Make a Variable using the token passed."""
        return Variable(tokens[0])
    
    @classmethod
    def make_set(cls, tokens):
        """Make a Set using the token passed."""
        return Set(*tokens[0])
    
    @classmethod
    def make_relational(cls, tokens):
        """Make a relational operation using the tokens passed."""
        left_op = tokens[0][0]
        operator = tokens[0][1]
        right_op = tokens[0][2]
        
        operation = cls.__operations__[operator]
        
        return operation(left_op, right_op)
    
    #{ Translators
    
    def represent_operand(self, operand):
        """
        Return the string representation of ``operand``.
        
        :param operand: The operand to be represented as a string.
        :type operand: :class:`booleano.operations.operands.Operand`
        :return: ``operand`` as a string.
        :rtype: unicode
        
        """
        if isinstance(operand, String):
            return self.represent_string(operand.constant_value)
        if isinstance(operand, Number):
            return self.represent_number(operand.constant_value)
    
    def represent_string(self, string):
        """
        Return ``string`` as a string quoted with ``T_STRING_START`` and
        ``T_STRING_END``.
        
        """
        return u'%s%s%s' % (self.T_STRING_START, string, self.T_STRING_END)
    
    def represent_number(self, number):
        """
        Return float ``number`` as a string and remove the decimals if it's
        an integer.
        
        """
        if not hasattr(number, "is_integer") or number.is_integer():
            number = int(number)
        return str(number)
    
    #}

