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
Source preprocessing

Preprocessing funcs are called
in the preprocess part of a text grammar.

Preprocess is particuliarly useful
to clarify the following grammar.

Here is just a set of useful functions:
  ~ NormalizeSeps: items such as whitespace or end of line,
    or any other kind of 'annoying' variable item,
    are normalized to a single form (eg ' ' or '\x0a').
    -- also useful to prepare SKIP_SEP mode (see config)
  ~ WrapIndentedStructure: replaces indented structure with
    wrapping block delimiters (eg '{' & '}' on their own line)
    -- then blocks are easily parsed
  ~ DeleteComments: removes comments from source,
    using start & end comment markers (often '#' & '\n').
  ~ DeleteBlankLines
  ~ ...

You can write your own custom transformations as needed:
include them in the <toolset> section of the grammar.
'''

# import export
from tools import *
from pattern import *
__all__ = ["NormalizeSeps",
           "WrapIndentedStructure",
           "IndentWrappedStructure"]


### character constants
(EOL, TAB, SPC, EOF) = ('\n', '\t', ' ', chr(3))


### separator normalization
def NormalizeSeps(source, format, standard=" "):
    ''' Normalize various separators matching format to standard value. '''
    from pijnu.generator.pijnuParser import format as formatPattern
    formatNode = formatPattern.parse(format)
    pattern = eval(formatNode.value)
    result = pattern.replace(source, standard)
    return result


### indented <--> wrapped structure
# tool funcs
def howManyAtStart(text, string):
    ''' how many times a (sub)string appears at start of text '''
    pos = 0
    n = 0
    length = len(string)
    while text[pos:].startswith(string):
        pos += length
        n += 1
    return n


def WrapIndentedStructure(source,
                          INDENT=None,
                          OPEN="{\n", CLOSE="}\n",
                          keepIndent=False):
    ''' Transform indented to wrapped structure.
        ~ Indentation must be consistent!
        ~ If INDENT not given, set to the first start-of-line whitespace.
        ~ Indentation can be kept: nicer & more legible result
          but needs to be coped with during parsing.
        ~ Blank lines are ignored. '''
    level = 0  # current indent level
    # add artificial EOFile marker
    source += EOF + EOL
    lines = source.splitlines()
    # find 'INDENT' indentation mark if not given
    if INDENT is None:
        for line in lines:
            if line.strip() == '':
                continue
            if line[0] == TAB:
                INDENT = TAB
                break
            n = howManyAtStart(line, SPC)
            if n > 0:
                INDENT = n * SPC
                break
    # case no indent at all
    if INDENT is None:
        return source
    # find indent level *changes* & replace them with tokens
    result = ""
    length = len(INDENT)
    for (i, line) in enumerate(lines):
        # skip blank line
        if line.strip() == '':
            if keepIndent:
                result += level * INDENT + EOL
            else:
                result += EOL
            continue
        # get offset: difference of indentation
        if line == EOF:
            line = ''
        offset = howManyAtStart(line, INDENT) - level
        # case no indent level change
        if offset == 0:
            result += line + EOL
        # case indent level increment (+1)
        elif offset == 1:
            level += 1
            open_mark = (INDENT * level + OPEN) if keepIndent else OPEN
            if not keepIndent:
                line = line[length:]
            result += open_mark + line + EOL
        # case indent level decrement (<= current level)
        elif offset < 0:
            offset = -offset
            level -= offset
            if keepIndent:
                close_marks = ""
                for n in range(level + offset, level, -1):
                    close_marks += (n * INDENT + CLOSE)
            else:
                close_marks = offset * CLOSE
                line = line[offset * length:]
            result += close_marks + line + EOL
        else:
            # case indent level inconsistency (increment > 1)
            message = "Inconsistent indentation at line #%s" \
                      " (increment > 1):\n%s" % (i, line)
            raise ValueError(message)
    return result


def IndentWrappedStructure(source, INDENT='    ', open="{", close="}"):
    ''' Transform wrapped to indented structure.
        ~ Wrapping must be consistent!
        ~ open/close tokens must be on an empty line! '''
    EOL = '\n'
    result = ""
    (pos, level) = (0, 0)  # current pos in text & indentation level
    lines = source.splitlines()
    for (i, line) in enumerate(lines):
        # case open
        if line.strip() == open:
            level += 1
        # case close
        elif line.strip() == close:
            if level == 0:
                message = "Inconsistent indentation at line #%s" \
                          " (decrement under zero):\n%s" % (i, line)
                raise ValueError(message)
            level -= 1
        # else record line with proper indentation
        else:
            result += level * INDENT + line.lstrip() + EOL
    return result


####### test #######
def testNormalize():
    source = "x x   x\tx\t\t\tx"
    format = "[ \t]+"
    print "\n=== normalize [ \\t]+ to '_' in source:\n   %s\n" \
            % repr(source)
    print NormalizeSeps(source, format, "_")


def testWrapIndent():
    # erroneous example
    source = """\
0
0
  1
      3
    2
  1
0
"""
    print "\n=== wrap indented blocks (erroneous case) in source:\n%s\n"\
            % (source)
    try:
        print WrapIndentedStructure(source, INDENT=None, keepIndent=True)
    except ValueError, e:
        print e
    # correct example
    source = """\
0
0
  1
  1
    2
    2
      3
      3
        4
          5
            6
      3
      3
  1
  1
0
0
"""
    print "\n=== wrap indented blocks (keeping indent) in source:\n%s\n"\
            % (source)
    result = WrapIndentedStructure(source, keepIndent=True)
    print result
    print "\n=== reindent same source"
    print IndentWrappedStructure(result)


def test():
    testNormalize()
    print RULER
    testWrapIndent()

if __name__ == "__main__":
    test()
