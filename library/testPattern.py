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
pattern testing
  -- in separate module to avoid parser circular import
'''

from parser import Parser   # for testing
from pattern import *


### test #####################################
def testCombine():
    print ("=== combine ===")
    # creation
    word1 = Word("abc")
    word2 = Word("def")
    sequence = Sequence((word1, word2))
    choice = Choice((word1, word2))
    combine = Sequence((sequence, choice, word1))
    parser = Parser(vars())
    #parser.collectPatterns()
    # output
    print (word1)
    print (word2)
    print (sequence)
    print (choice)
    print (combine)
    Pattern.FULL_OUTPUT = True
    print (combine)
    Pattern.FULL_OUTPUT = False
    # successful match
    print ("=== success")
    word1.test("abcde")
    word1.memo=dict()
    choice.test("def")
    word1.memo=dict()
    word2.memo=dict()
    sequence.test("abcdefghi")
    combine.test("abcdefdefabcXXX")
    # failure matches
    print ("=== failure")
    word1.memo=dict()
    word1.test("Xbcde")
    word1.memo=dict()
    word2.memo=dict()
    choice.test("Xbc")
    combine.test("abcdefabcdefXXX")


def testPossib():
    print ("=== 'possibilities' ===")
    # creation
    word = Word("abc")
    option = Option(word)
    next = Next(word)
    nextNot = NextNot(word)
    parser = Parser(vars())
    text1, text2 = "abcX", "Xabc"
    print "wrapped pattern:   %s" %word
    # successful match
    print ("=== success")
    option.test(text1)
    next.test(text1)
    nextNot.test(text2)
    # failure matches
    print ("=== failure")
    option.test(text2)
    next.test(text2)
    nextNot.test(text1)


def testRepete():
    print ("=== repete ===")
    # creation
    word = Word("zzz")
    zeroOrMore = ZeroOrMore(word)
    oneOrMore = OneOrMore(word)
    repete3 = Repetition(word, 3, 3)
    repete13 = Repetition(word, 1, 3)
    repete03 = Repetition(word, 0, 3)
    repeteStar = Repetition(word, False, False)
    repetePlus = Repetition(word, 1, False)
    repete2Plus = Repetition(word, 2, False)
    parser = Parser(vars())
    textNil, text0, text1, text3 = "", "X", "zzzX", "zzzzzzzzzX"
    print "wrapped pattern:   %s" %word
    # matches
    print ("=== matches for several length")
    zeroOrMore.test(text3)
    zeroOrMore.test(text1)
    zeroOrMore.test(text0)
    zeroOrMore.test(textNil)
    oneOrMore.test(text3)
    oneOrMore.test(text1)
    oneOrMore.test(text0)
    oneOrMore.test(textNil)
    repete13.test(text3)
    repete13.test(text1)
    repete13.test(text0)
    repete13.test(textNil)
    repete3.test(text3)
    repete3.test(text1)
    repete03.test(text0)
    repeteStar.test(text0)
    repetePlus.test(text0)
    repetePlus.test(text3)
    repete2Plus.test(text1)
    repete2Plus.test(text3)


def testChars():
    print ("=== char based ===")
    # creation
    a = Char('a')
    aaa = OneOrMore(a)
    klass = Klass(r"a..z  A..Z  0..9  +-*/  ]\t\\  !!kq  B..Y  0")
    klassN = Klass("a..zA..Z")
    string = String(klassN, numMin=1, numMax=9)
    parser = Parser(vars())
    # char matches
    print ("=== char matches")
    a.test('az')
    a.test('za')
    aaa.test('aaaz')
    # klass matches
    print ("=== klass matches")
    print "pattern   %s" % klass
    for source in ("a", "q", "A", "B", "1", "0", "*", "\\", "]", "[", "&", ""):
        try:
            result = klass.match(source)
        except EndOfText:
            result = "<EndOfText>"
        except MatchFailure:
            result = "<MatchFailure>"
        print "   %5s --> %s" % (repr(source), result)
    # string expression
    print ("=== numbered string format expression")
    k = Klass('z')
    print "False, False -->", String(k, False, False)._format()
    print "0, False -->", String(k, 0, False)._format()
    print "False, 0 -->", String(k, False, 0)._format()
    print "0, 0 -->", String(k, 0, 0)._format()
    print "1, False -->", String(k, 1, False)._format()
    print "1, 0 -->", String(k, 1, False)._format()
    print "3, False -->", String(k, 3, False)._format()
    print "3, 0 -->", String(k, 3, False)._format()
    print "3, 3 -->", String(k, 3, 3)._format()
    print "3, 7 -->", String(k, 3, 7)._format()
    print "0, 7 -->", String(k, 0, 7)._format()
    # string matches
    print ("=== string matches")
    String(klassN, 0, 0).test("abc#")
    String(klassN, 0, 0).test("#abc#")
    String(klassN, 1, 0).test("abc#")
    String(klassN, 1, 0).test("#abc#")
    String(klassN, 5, 0).test("abcefghij#")
    String(klassN, 5, 0).test("abc#")
    String(klassN, 5, 0).test("abc")
    for source in   (
                    "Yabc#",
                    "abc",
                    "abcqkabc",
                    "a\\\]\t789",
                    "1+2*3",
                    "abc#",
                    "#abc",
                    "abcdefghijklmno",
                    "a",
                    ""
                    ):
        string.test(source)


def testRecursion():
    print ("=== recursion ===")
    ### self recursion
    # x : ('a' x) / 'a'   <=>   x : 'a'+
    l       = Char('a')
    x       = Recursive()
    ll      = Sequence([l, x])(join)
    x       **= Choice([ll, l])

    # y : '(' y ')' / 'a'  -- y::(parenY / l)
    (lparen, rparen) = (Char('(')(drop), Char(')')(drop))
    y       = Recursive()
    parenY  = Sequence([lparen, y, rparen])
    y       **= Choice([parenY, l])

    ### mutual recursion
    # grp   : '(' oper ')'
    # oper  : (group / num) '*' (group / num)
    n       = Char('1')(toInt)
    op      = Char('~')
    grp     = Recursive()
    oper    = Sequence([Choice([grp, n]), op, Choice([grp, n])])(extract)
    grp     **= Sequence([lparen, oper, rparen])

    # mult  : (group / n) '*' (group / mult / n)
    # add   : (mult / n) '*' (add / mult / n)
    # group : '(' (add / mult) ')'
    group   = Recursive()
    add     = Recursive()
    mult    = Recursive()
    star    = Char('*')
    plus    = Char('+')
    mult    **= Sequence([Choice([group, n]), star, Choice([group, mult, n])])(extract)
    add     **= Sequence([Choice([mult, n]), plus, Choice([add, mult, n])])
    group   **= Sequence([lparen, add, rparen])
    formula = Choice([add, mult, n])

    parser = Parser(vars())

    # testing
    print ("=== auto recursion")
    x.test("a  aaa  baab  aaaaa", "findAll")
    y.test("a  (a)  (((a)))  ()", "findAll")
    print ("=== mutual recursion")
    oper.test("1~1  (1~1)~1  1~(1~1)  (1~1)~(1~1)", "findAll")
    formulas = "1  1*1  1*1*1  1*(1+1)  1+1  1+1+1  1+(1+1)*1  (1+1)*(1+1)+1"
    formula.test(formulas, "findAll")


def testFindReplace():
    text = "qoi2156g564grf88ze"
    print "\n=== findAll [0..9]+ in\n   %s\n" % text
    num = String(Klass("0..9"))
    num.name = "num"
    print num.findAll(text)
    print "\n=== replace [0..9]+ with '#' in\n   %s\n" % text
    print num.replace(text, "#")


def test():
    testCombine()
    print RULER
    testPossib()
    print RULER
    testRepete()
    print RULER
    testChars()
    print RULER
    testRecursion()
    print RULER
    testFindReplace()
    pass

if __name__ == "__main__":
    test()
