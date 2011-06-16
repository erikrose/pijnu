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


from pijnu.library import *

testingParser = Parser()
state = testingParser.state

### title: testing ###
###   <definition>
# recursive pattern(s)
# codes
# patterns
# top pattern
AorBorC = Klass('ABC', expression='[ABC]', name='AorBorC')

testingParser._recordPatterns(vars())
testingParser._setTopPattern("AorBorC")
testingParser.grammarTitle = "testing"
testingParser.filename = "testingParser.py"

# ===================================================================

AorBorC.test('A$')
AorBorC.test('X$')

test_dict = AorBorC.testSuiteDict(['A$', 'B$', 'C$', 'X$', '0$'])
AorBorC.testSuite(test_dict)
