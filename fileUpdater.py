#! /usr/bin/env python
# coding:utf8

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

''' tool prog to insert a notice in selected files of recursively walked dirs
	
		See more info in variable 'info' below.
	'''

from pijnu.tools import fileText, fileNames
import sys, os
end = sys.exit

# tool func to replace or remove specific text in files
def changeText(filename, text,newtext=""):
	''' *Change* (or *remove*) text in this file.
		-- called by changeFiles '''
	filetext = fileText(filename)
	if text in filetext:
		filetext = filetext.replace(text, newtext)
		f = file(filename, 'w')
		f.write(filetext)
		f.close()
		print "file: %s" % filename
def changeTexts(text, newtext="", dir=None, ext="py"):
	# parameters
	if dir is None: dir = os.getcwd()
	# run
	print "=== file walk ==="
	filenames = fileNames(dir, ext)
	print "\n=== changing files ==="
	for filename in filenames:
		changeText(filename, text,newtext)

# tool func to insert notice in files
def insertNotice(filename, notice, linecount):
	''' Insert notice in this file. '''
	notice_lines = ["%s\n" % l for l in notice.splitlines()]
	# compose new text version
	filelines = file(filename).readlines()
	textlines = filelines[0:linecount] + notice_lines + filelines[linecount:]
	text = "".join(textlines)
	# write it back
	f = file(filename, 'w')
	f.write(text)
	f.close()
	print "file: %s" % filename
def insertNotices(notice_filename, linecount=2, dir=None, ext="py"):
	# params
	if dir is None: dir = os.getcwd()
	try:
		notice = fileText(notice_filename)
		notice_start = '\n'.join(notice.splitlines()[:7])
	except IOError:
		notice = notice_start = None
	# now, run?
	print (	"\ndir: %s\next: %s\nlinecount: %s\nfirst text lines:\n%s\n"
			% (dir, ext, linecount, notice_start) )
	answer = raw_input(">>> write notice in files? (y/n)")
	if not (answer.lower() == 'y'):
		end()
	# yes, run!
	print "=== file walk ==="
	print linecount, dir
	filenames = fileNames(dir, ext)
	print "\n=== writing notice ==="
	for filename in filenames:
		insertNotice(filename, notice, linecount)

