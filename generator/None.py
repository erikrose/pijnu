""" genTest
<definition>
X	: 'x'
XX	: X XXX			: join
XXX	: XX / X		: @

"""



from pijnu.library import *

genTestParser = Parser()
state = genTestParser.state




### title: genTest ###


###   <toolset>
pass

###   <definition>
# recursive pattern(s)
XXX = Recursive(name='XXX')
X = Char('x', expression="'x'",name='X')
XX = Sequence([X, XXX], expression='X XXX',name='XX')(join)
XXX **= Choice([XX, X], expression='XX / X',name='XXX')



genTestParser._recordPatterns(vars())
genTestParser._setTopPattern("XXX")
genTestParser.grammarTitle = "genTest"
genTestParser.filename = "None.py"
