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
Match errors

pijnu errors -- with full information output
'''


### import/export
from tools import *

__all__ = ["PijnuError", "ErrorLocation",
           "MatchFailure", "EndOfText", "IncompleteParse", "Invalidation"]


class PijnuError(Exception):
    ''' pijnu top error'''
    LINE = 33 * '*'


class ErrorLocation(object):
    ''' textual and visual information about
    failure location in source string
    '''
    def __init__(self, source, pos):
        ''' Record info. '''
        self.source = source
        self.pos = pos  # base index 0!
        self.text = self._text(source, pos)
        self.visu = self._visu(source, pos)

    def _text(self, source, pos):
        ''' textual location: index, line #, char # '''
        source_upto = source[:pos]
        # line number holding current char
        line_no = source_upto.count(NL) + 1
        # char number inside current line
        if line_no == 1:
            char_no = pos + 1
        else:
            char_no = pos - source_upto.rindex(NL)
        # textual location
        return "index #%d   line %d   character %d" % (pos, line_no, char_no)

    def _visu(self, source, pos):
        ''' visual location '''
        source_upto = source[:pos]
        source_from = source[pos:]
        # replace control chars by their repr() to avoid visual mess
        source_upto = ErrorLocation._cleanRepr(source_upto)
        source_from = ErrorLocation._cleanRepr(source_from)
        # trunc if too long
        length = len(source_upto)
        source_upto = source_upto[length - 33:length]
        source_from = source_from[:33]
        # build visual
        pointer = len(source_upto) * SPC + '^'
        return "   %s%s\n   %s" % (source_upto, source_from, pointer)

    # tool func for clean text output
    control_chars = set(chr(n) for n in (range(0, 32) + range(127, 160)))
    control_char_map = dict((c, repr(c)[1:-1]) for c in control_chars)

    @staticmethod
    def _cleanRepr(text):
        ''' text with control chars replaced by repr() equivalent '''
        chars = ""
        for char in text:
            if char in ErrorLocation.control_chars:
                char = ErrorLocation.control_char_map[char]
            chars += char
        return chars

    def __str__(self):
        ''' location feedback '''
        return "%s%s\n%s" % (SPC3, self.text, self.visu)


class MatchFailure(PijnuError):
    ''' standard match failure exception
    Used mainly to provide worthful feedback.
    '''
    def __init__(self, pattern, source, pos, wrap=False):
        ''' Record data. '''
        self.pattern = pattern
        self.source = source
        self.pos = pos
        # wrap is used to avoid printing full error frame
        # for wrapped errors raised by wrapped pattern
        self.wrap = wrap

    def __str__(self):
        ''' failure feedback:
            ~ pattern
            ~ location
            ~ reason
            Possibly information transfered from sub pattern failure(s). '''
        self.message = self.pattern._message()
        self.location = ErrorLocation(self.source, self.pos)
        if self.wrap:
            return ("\nMatch failure for pattern\n"
                    "%s%s\n"
                    "in source text at location\n"
                    "%s\n"
                    "%s"
                    % (SPC3, self.pattern,
                        self.location,
                        self.message))
        return ("\n%s\n"
                "Match failure for pattern\n"
                "%s%s\n"
                "in source text at location\n"
                "%s\n"
                "%s\n"
                "%s"
                % (self.LINE,
                    SPC3, self.pattern,
                    self.location,
                    self.message,
                    self.LINE))


class EndOfText(PijnuError):
    ''' standard parse failure exception
        Used to avoid worse placeholder and provide feedback.
        '''
    def __init__(self, pattern, source, wrap=False):
        ''' Record data. '''
        self.pattern = pattern
        self.source = source
        # wrap is used to avoid printing full error frame
        # for wrapped errors raised by wrapped pattern
        self.wrap = wrap

    def __str__(self):
        ''' failure feedback:
            ~ pattern
            ~ reason
            ~ location
            Possibly information transfer from sub pattern failure(s). '''
        source = self.source
        self.location = ErrorLocation(source, len(source))
        if self.wrap:
            return ("\nMatch failure for pattern:\n"
                    "%s%s\n"
                    "in source text at location\n"
                    "%s\n"
                    "Reached end of source text."
                    % (SPC3, self.pattern, self.location))
        return ("\n%s\n"
                "Match failure for pattern:\n"
                "%s%s\n"
                "in source text at location\n"
                "%s\n"
                "Reached end of source text.\n"
                "%s"
                % (self.LINE, SPC3, self.pattern, self.location, self.LINE))


class IncompleteParse(PijnuError):
    ''' incomplete parse exception
        Used with 'parse' & 'parseTest' methods
        when not whole of text is matched.
        '''

    def __init__(self, pattern, source, pos, result):
        ''' Record data. '''
        self.pattern = pattern
        self.source = source
        self.pos = pos
        self.result = result

    def __str__(self):
        ''' failure feedback:
            ~ pattern
            ~ location '''
        self.location = ErrorLocation(self.source, self.pos)
        return ("\n%s\n"
                "Parse failure for pattern\n"
                "%s%s\n"
                "Cannot match whole of source text.\n"
                "Matching stopped at location\n"
                "%s\n"
                "Partial result is\n"
                "%s%s\n"
                "%s"
                % (self.LINE,
                  SPC3, self.pattern,
                  self.location,
                  SPC3, self.result,
                  self.LINE))


class Invalidation(PijnuError):
    ''' validation lack exception
        To be used by transformation funcs that actually validate a match:
            * typically context/state dependant matches
            * or expressions too complicated for a pattern
        ~ See note in __init__ about parameter 'message'.
        '''

    def __init__(self, message, pattern=None,
                 source=None, pos=None, wrap=False):
        ''' Record data.
        ~ The 'message' parameter should be clear enough!
        ~ The caller may provide pattern for message output.
        ~ The caller may provide location for message output through
          paraneters 'source' & 'pos'.
        ~ Both can be combined:
            message = "........."
            (pattern,pos,source) = (node.pattern,node.start,node.source)
            raise Invalidation(message, pattern=pattern, source=source,pos=pos)
            '''
        self.message = message
        # pattern?
        if pattern is None:
            self.has_pattern = False
        else:
            self.has_pattern = True
            self.pattern = pattern
        # location?
        if source is None or pos is None:
            self.has_location = False
        else:
            self.has_location = True
            self.source = source
            self.pos = pos
        # wrap is used to avoid printing full error frame
        # for wrapped errors raised by wrapped pattern
        self.wrap = wrap

    def __str__(self):
        ''' failure feedback: provided by the caller '''
        # pattern text?
        if self.has_pattern:
            noValidText = ("Invalidation failure for pattern \n%s%s\n"
                           % (SPC3, self.pattern))
        else:
            noValidText = "Invalidation failure.\n"
        # location?
        if self.has_location:
            location = ErrorLocation(self.source, self.pos)
            locationText = "in source text at location\n%s\n" % location
        else:
            locationText = ""
        # whole message
        if self.wrap:
            return "\n%s%s%s" % (noValidText, locationText, self.message)
        return ("\n%s\n%s%s%s\n%s"
                % (self.LINE, noValidText, locationText, self.message, self.LINE))
