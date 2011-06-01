# -*- coding:utf-8 -*-


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
from pijnu.generator import writeParser
grammar = file("standard.pijnu").read()
writeParser(grammar)
from standardParser import standardParser as p
n = p.number

print p.integral_part
sources = "1 1,123 1,23 1.1 1. 0,123,456,789 1,23,456,789 0,123,456.789 -0,123,456.789 -1.1".split()
n.testSuiteDict(sources)

#~ from pijnu.library import *
#~ i = Repetition(Char('1'), numMin=3,numMax=3)
#~ i.test("11")
