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
Simple test profiler -- just case needed
'''

from pijnu import makeParser


def parseTest():
    numbersTransformGrammar = """\
numbersTransform
<toolset>
def toReal(node):
	node.value = float(node.value)
<definition>
SEP			: ' '						: drop
DOT			: '.'
digit		: [0..9]
integer		: digit+					: join
real		: integer DOT integer?		: join
number		: real / integer			: toReal
addedNum	: SEP number				: liftNode
numbers		: number (addedNum)*		: extract
"""
    makeParser(numbersTransformGrammar)


def profile(command, logFile):
    import cProfile
    import pstats
    ruler = 33 * "="
    # run with profiler & timer
    cProfile.run(command, logFile)
    print ruler
    ps = pstats.Stats(logFile)
#~  ps.strip_dirs()
    ps.sort_stats("time")
    ps.print_stats(11)
    print ruler

profile("parseTest()", "testProfileStats")
