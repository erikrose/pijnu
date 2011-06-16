# -*- coding: utf8 -*-

'''
© 2009 Denis Derman (former developer) <denis.spir@gmail.com>
© 2011 Peter Potrowl (current developer) <peter017@gmail.com>

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

'''
Character klass parsing & expansion to produce a character set

    Note:
    This is used only for a "manual" klass pattern in python code.
    Klass expression charset are produced using step-by-step
    transformation of char formats, ranges, and whole klass.

    format
    similar to regex [...] charset
    differences intended for legibility:
    * range code is '..' (instead of '-')
    * double space '  ' is used as optional visual separator
    * no leading negation code '!'
    * instead trailing exclusion using '!!'
    [a..z  A..Z  !!kqKQ]

    Note:
    As it is nonsense to include twice the same character in a charset,
    the use of double characters as special codes is safe,
    and avoids useless escaping of ' ', '.', & '!'.

    valid character formats by default:
    * literal 'safe' char: no \, TAB, NL, CR, ', ", ]
    * hex ordinal: '\x2f'  -- 2 hex digits
    * dec ordinal: '\047'  -- 3 dec digits
    * python-like code: \t \n \r \\ \] \' \"

range expression:
    <char>..<char>
    * <char> can be any of the above character formats
    * If the second char's ordinal is less than the first one's,
        the expansion returns an empty set (no exception).

use of double space as visual separator:
    "a..e  1..9"		--> "abcde123456879_ "
    "abc  _  +-*/"		--> "abc_+- */"

char klass expression in python code:
    pattern = Klass(".........")
    * Klass automatically calls charset() when not produced
        by the generator (ie not from text grammar).
    * For python, possible quotes in klass expression must be escaped;
        use triple quoted strings instead to avoid this issue:
        """+-*/  '"  0..9"""
    * For python again, possible '\' (either as literal or to express
        character code) must be escaped (or double escaped):
        use raw strings instead:
        r"""/\|  \t\r\n  \009..\013  \x20\x28"""
    * If triple quoted raw strings are used, then the
        expression is identical to the one in text grammar.
        (except right bracket needs not be escaped in code).
    * This allows you to use spaces for legibility,
        even in klass expressions with no range:
        "abc  +-*/  12345"
    * You can of course call charset() manually to build charsets.
        In this case, you can pass both the expression and the charset:
        Klass(expression, charset)
'''


# import export
from sys import exit as end, stderr as error
import re
pattern = re.compile
__all__ = ["charset_names", "charset", "seqCharset"]
charset_names = __all__


# constant to be used in charset call
FROM_TEXT = True

# regex pattern for any valid char format:
# hex ordinal | dec ordinal | range code | literal char
#	~ hex ordinal	:	\\x[\da-fA-F]{2}
#	~ dec ordinal	:	\\[\d]{3}
#	~ range code	:	\.\.
#	~ literal char	:	\n|.
# Coded characters (\\ \t \n \r \] \' \") are replaced directly.
char = pattern(r"(\\x[\da-fA-F]{2})|(\\[\d]{3})|(\.\.)|(.|\n)")

# character format converter
RANGE_MEMO = ""		# used to "remember" range code position


def literalChar(result):
    ''' return literal character from any valid character format:
        * hex ordinal: \Xhh
        * dec ordinal: \ddd
        * range code: '..'
        * literal safe char: any non-escaped char '''
    hex, dec, range, lit = result
    if hex:
        return chr(int(hex[2:], 16))
    elif dec:
        return chr(int(dec[1:]))
    elif range:
        return RANGE_MEMO
    else:
        return lit


# range expansion
def expandedSeq(seq):
    ''' return character sequence with expanded ranges '''
    while RANGE_MEMO in seq[1:-1]:
        pos = seq.index(RANGE_MEMO, 1, -1)
        (pos1, pos2) = (pos - 1, pos + 1)
        (ord1, ord2) = (ord(seq[pos1]), ord(seq[pos2]))
        char_range = [chr(n) for n in range(ord1, ord2 + 1)]
        seq[pos1:pos2 + 1] = char_range
        #~~print "range: pos=%s [%s..%s] [%s..%s] =>\n%s" \
        #% (pos,seq[pos1],seq[pos2],ord1,ord2,char_range)
    return seq


# production of charset from cleant expression
def production(expression):
    try:
        # regex parsing --> char sequence
        format_charseq = char.findall(expression)
        # convert to literal character sequence
        # (+ possible ranges codes)
        charseq = [literalChar(c) for c in format_charseq]
        # expand character ranges
        expanded_charseq = expandedSeq(charseq)
        # glue the seq into a string
    except Exception, error_text:
        message = "Invalid charset expression:"
        cause = "%s\n   %s\n%s" % (message, expression, error_text)
        raise ValueError(cause)
    return "".join(expanded_charseq)


#replace coded chars
def codesToChars(expression):
    expression = expression.replace("\\\\", '\\')
    expression = expression.replace("\\t", '\t')
    expression = expression.replace("\\n", '\n')
    expression = expression.replace("\\r", '\r')
    expression = expression.replace("\\'", '\'')
    expression = expression.replace("\\\"", '"')
    expression = expression.replace("\\]", ']')
    return expression


# exclusion
def exclusionSet(inset, exset):
    for c in exset:
        inset = inset.replace(c, '')
    return inset

# global func
EXCLUSION = "!!"
SPACE2 = "  "


def charset(expression):
    ### cleaning phase:
    #	~ double space separators are erased
    #	~ nesting brackets are dropped
    #	~ replace python-like code: \t \n \r \\, plus \] \' \"
    expression = expression.replace(SPACE2, "")
    if len(expression) > 2 and expression[0] == "[" and expression[-1] == "]":
        expression = expression[1:-1]
    expression = codesToChars(expression)

    ### processing phase
    # if expression contains EXCLUSION code '!!', split it
    # and produce both included and excluded charsets
    #   [included!!excluded]
    # then remove excluded characters
    if EXCLUSION in expression:
        (included, excluded) = expression.split(EXCLUSION)
        (inset, exset) = (production(included), production(excluded))
        return exclusionSet(inset, exset)
    # else simply production whole whole
    return production(expression)


# === test ==================================================
# tool func
RULER = 33 * '='


def trial(expression):
    print RULER
    print ("expression str:\n'%s'\nexpression repr:\n%s\n"
        % (expression, repr(expression)))
    charstring = charset(expression)
    print ("charset str:\n'%s'\ncharset repr:\n%s"
        % (charstring, repr(charstring)))
    print RULER


def test():  # causes error at the end
    # backslashes must not be escaped in raw string
    # works fine for single spaces too
    # 'X\\\\ \\ \a\\a\*\\*X'
    expression = r"""X\  \\  \   \\   \a  \\a  \*  \\*X"""
    trial(expression)
    # use python codes -- but no double backslashes!
    # insert quotes in triple quoted string
    # 'X\t\r\n\\'""'\\t\\r\\n\\\\X'
    expression = r"""X\t\r\n\\  '""'  \\t\\r\\n\\\\X"""
    trial(expression)
    # possibly wrap expression inside []
    # possibly escape ']'
    # 'X123\]\\]abcX'
    expression = r"""[X123  \]\'\"  \\]\\'\\"  abcX]"""
    trial(expression)
    # double space separator (2 first dots disappear,
    # cause double spaces are erased, so dot are like range code)
    # ' . .'
    expression = r""".    . .       ."""
    trial(expression)
    # homogeneous range
    # '123451234512345'
    expression = r"""1..5  \049..\053  \x31..\x35"""
    trial(expression)
    # heterogeneous range
    # '123451234512345'
    expression = r"""1..\053  \049..\x35  \x31..5"""
    trial(expression)
    # single, zero or reversed range
    # '3'
    expression = r"""3..3  3..2  3..1"""
    trial(expression)

    # exclusion
    # 'abcdefghijlmnoprstuvwxyzAZ123456789'
    expression = r"""[a..z  A..Z  0..9  !!kq  B..Y  0]"""
    trial(expression)
    # error !!!
    expression = r"""abc\999k..xyz"""  # causes error!
    trial(expression)
if __name__ == "__main__":
    test()
