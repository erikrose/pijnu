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
Patterns

    This is the core module.
    Holds all sorts of pattern types used to perform matches.
    An individual pattern instance corresponds to a pattern in text parser
    specified with various parameters depending on the kind of pattern.

    The "engine" of a pattern is its _realCheck method (not to call directly).
    This is used by the various match forms available to the user:
        * match: try & match at start of source
        * parse: try & match the whole source
        * findFirst: try & find a match anywhere in source
        * findall: idem, & return a sequence of match nodes
        * replace: find all & replace matches with new string - see details

    PEG / packrat peculiarities:
        * A PEG parser is not a generative parser like E/BNF or regex.
          Instead, it displays the format, how to distinguish it.
          It actually represents a parse algorithm, hence its interest.
        * Especially, a choice '/' is a real prioritized alternation
          that avoids common complication. This comes to the price of higher
          complication in more rare cases -- see 'lookahead' & 'Until'.
        * The packrat algorithm allows a linear parse time -- proportional
          to source size. This is ensured by "memoïzing" match checks in
          order to avoid repetitive trials at the same position in source.
        * See internet literature for more details.

    ~ super type: Pattern
    ~ base PEG patterns:
        * literal/terminal: Word ("...")
        * combinators: choice Choice (/), sequence Sequence ( )
        * option & repetitions: Option (?), ZeroChoiceMore (*) OneChoiceMore (+)
        * lookahead: positive Next (&), negative NextNot for (!)
        * Charset: Klass ([...]) -- see details in code
        * AnyChar (.) -- ditto
    ~ additional patterns:
        * character specific patterns:
          Char ('°'), Klass([...]), String ([...]*/+/{m,n})
        * Recursive -- implementation trick
        * "stop condition": Until pattern wrapper (/)
        * value equality check: Equals pattern wrapper (=)
        * number repetition: Repetition ({n} or {m,n})

    See also:
        * preprocessing module
        * value transformation and value object in Node module

    Kind of patterns. There are basically:
        ~ Raw or 'terminal' patterns that actually match source characters
          (and can actually fail).
          These are Word and character specific patterns.
        ~ Wrapper or 'stuctural' patterns that organise raw patterns.
          They rather transfer result nodes or match failure.
          These are .
'''


### import/export
from tools import *

from node import *
from error import *
from charset import charset as toCharset
from time import time   # for stats


# object used to collect statistics on match checks
class Stats(object):
    ''' object used to collect statistics on match checks
    '''
    def __init__(self, start_time=None):
        self.start_time = start_time
        self.stop_time = None
        self.trials = 0
        self.memos = 0
        self.checks = 0
        self.failures = 0
        self.matchFailures = 0
        self.EOTs = 0
        self.invalids = 0
        self.successes = 0
        self.branches = 0
        self.leaves = 0

    def time(self):
        if self.start_time is None or self.stop_time is None:
            return ""
        runtime = self.stop_time - self.start_time
        return "\nrun time: %.3f" % runtime

    def __str__(self):
        return ("\n=== parsing statistics:\n"
                "match trials:          %s\n"
                "   memos:              %s\n"
                "   checks:             %s\n"
                "       failures:       %s\n"
                "           matchFails: %s\n"
                "           EOTs:       %s\n"
                "           invalids:   %s\n"
                "       successes:      %s\n"
                "           branches:   %s\n"
                "           leaves:     %s\n"
                "%s"
                %(
                self.trials,self.memos,self.checks,
                self.failures,self.matchFailures,self.EOTs,self.invalids,
                self.successes,self.branches,self.leaves,
                self.time()
                )
        )


### super type ###
class Pattern(object):
    ''' pattern object
        ~ name: --> node type
        ~ memo: packrat memoïzing
        ~ view: name:format
        Each pattern type holds (at least) its own:
            * __init__: specific parameters
            * _realCheck: perform actual match trial
            * _message: error output
            * __str__: output format
        Wrapping patterns also have:
            * _fullStr: for full subpattern output format
    '''

    # statistics on match checks --see class Stats
    stats = Stats()

    ### config & constants
    # extensive output for sub-patterns, else name only
    FULL_OUTPUT = False
    # unused yet
    TEST_MODE = False
    # collect statistics on match checks
    DO_STATS = False
    # unnamed pattern default name
    DEFAULT_NAME = "<?>"

    ### creation
    def __init__(self, expression=None, name=None):
        ''' Common pattern intialization:
            format, name, transformations, memoïzation
        '''
        # format:
        # ~ from text grammar: format is taken from original expression
        # ~ from source code: a normal format is computed
        #   according to pattern type, at first request for ouput
        #   [because of (possibly wrapped) recursive patterns
        #   which are not defined at object creation time].
        self.format = expression
        # name is set later via parser.collectPatterns() or manually
        self.name = Pattern.DEFAULT_NAME if name is None else name
        # actions are set via __call__ (syntactic trick)
        self.actions = None      # --> node value transformation
        # parser is set later via parser.collectPatterns()
        self.parser = None          # unused yet
        # memoization
        self.memo = dict()          # --> packrat memoïzation
        self.wrapped = []           # --> _resetMemo

    ### match methods
    # matchTest & parseTest methods perform in test mode:
    #   ~ in case of failure, output error and continue
    #   ~ very handy for sequence of tests
    def match(self, source):
        ''' Match start of source text.
            Return result tree/node or raise MatchFailure error.
        '''
        # reset memoization of all patterns involved, recursively
        self._resetMemo()

        # match
        return self._memoCheck(source, 0)

    def matchTest(self, source):
        ''' Match in test mode. '''
        # match
        try:
            return self.match(source)
        except PijnuError, e:
            print (e)
            return None

    def parse(self, source):
        ''' Match whole of source text.
            Return result tree/node or raise MatchFailure error.
        '''
        if Pattern.DO_STATS: Pattern.stats.__init__(time())
        # reset memoization of all patterns involved, recursively
        self._resetMemo()

        # parse
        result = self._memoCheck(source, 0)
        if Pattern.DO_STATS:
            Pattern.stats.stop_time = time()
            print Pattern.stats

        # case whole of source text is matched
        pos = result.end
        if pos == len(source):
            return result

        # case matching stopped before end of source text
        raise IncompleteParse(self, source, pos, result)

    def parseTest(self, source):
        ''' Parse in test mode.
        '''
        try:
            return self.parse(source)
        except (MatchFailure,EndOfText,IncompleteParse), e:
            print (e)
            return None

    def findFirst(self, source):
        ''' Find & return first match for pattern in source.
            ~ case no match found, return None
        '''
        # reset memoization of all patterns involved, recursively
        self._resetMemo()

        # lookup first occurrence
        length = len(source)
        pos = 0
        while pos < length:
            try:
                return self._memoCheck(source, pos)
            except PijnuError:
                pos += 1
        return None

    def findAll(self, source):
        ''' Find & return all matches for pattern in source ~ findAll.
            ~ Case none is found, result is empty sequence.
            ~ Overlapping matches are not twice collected.
            ~ findAll does *not* collect nil nodes!
        '''
        # reset memoization of all patterns involved, recursively
        self._resetMemo()

        # lookup all occurrences
        nodes = Seq()
        length = len(source)
        pos = 0
        while pos < length:
            try:
                node = self._memoCheck(source, pos)
                # beware of successful node without advance !!! (eg Option)
                if node.value == Node.NIL:
                    pos +=1
                else:
                    pos = node.end
                    nodes.append(node)
            except PijnuError:
                pos += 1
        return nodes

    def replace(self, source, value):
        ''' Find all matches for pattern in source
            & replace them with given value.
            ~ uses findAll
        '''
        # reset memoization of all patterns involved, recursively
        self._resetMemo()

        # lookup & replace
        result = ''
        nodes = self.findAll(source)
        pos = 0
        for node in nodes:
            result += source[pos:node.start] + value
            pos = node.end
        result += source[pos:]
        return result

    # memoization reset
    def _resetMemo(self, done=None):
        ''' Reset memoization of all patterns involved, recursively.
        '''
        if done is None: done = list()

        # reset self memo
        self.memo = dict()
        done.append(self)

        # recursive memo reset of not-yet-reset wrapped pattern(s)
        # (works for recursive patterns as well)
        for p in self.wrapped:
            if p not in done:
                p._resetMemo(done)

    ### test a pattern -- or a parser
    # 'test' performs test match using given method
    # and outputs legible result -- Use it!!!
    def test(self, source, method_name="matchTest"):
        ''' Try performing test match on source text;
            output match summary in nice format and return result.
            In case of success, result is generated node.
            In case of error, result is None & error is also printed out.
            Note that unlike testSuite, the default method is match.
        '''
        # match trial
        method = getattr(self, method_name)
        result = method(source)

        # output
        LINE = 33 * '-'
        result_text = "<None>" if result is None else result.treeView()
        print( "%s\npattern:  %s\nsource:   %s\nmethod:   %s\nRESULT:\n%s\n%s"
                % (LINE,self,repr(source),method_name,result_text,LINE) )

        # if ever...
        return result

    def testSuite(self, test_dict, method_name="parse", verbose=False):
        ''' Perform a test suite by asserting equality
            of expected and actual parse results.
            This method is rather intended to check that modifications
            did not create bugs, after a program has once run fine.
            ~  test_dict holds {source:result} pairs
            ~ result is in fact the string repr of a node *value*
            ~ None result means expected failure.
            Use testSuiteDict to first get a test_dict.
            Note that unlike test, the default method is parse.
            '''
        # get proper match method
        method = getattr(self, method_name)
        # perform matches and assert
        error_count = 0
        pass_count = 0
        for (source, result) in test_dict.items():
            try:
                r = method(source).value
            except PijnuError:
                r = None
            try:
                assert unicode(r) == result
                if verbose:
                    print "%s --> %s" %(source, result)
                pass_count += 1
            except AssertionError:
                error_count += 1
                print ("*** error ***\n   %s --> %s\n   expected: %s"
                       % (source, unicode(r), result))
        # print summary
        print "\n*** Test suite: %s passed; %s failed ***" % (pass_count, error_count)
        return error_count

    def testSuiteMultiline(self, sources, results, method_name="parse", verbose=False):
        ''' Perform a test suite by asserting equality
            of expected and actual parse results.
            This method is rather intended to check that modifications
            did not create bugs, after a program has once run fine.
            ~  test_dict holds {source:result} pairs
            ~ result is in fact the string repr of a node *value*
            ~ None result means expected failure.
            Use testSuiteDict to first get a test_dict.
            Note that unlike test, the default method is parse.
            '''
        assert len(sources) == len(results), "Bad length: %s sources for %s results!" % (len(sources), len(results))
        # get proper match method
        method = getattr(self, method_name)
        # perform matches and assert
        error_count = 0
        pass_count = 0
        for i in range(len(sources)):
            source = sources[i]
            result = results[i]
            try:
                r = method(source)
            except PijnuError:
                r = None
            try:
                assert r.treeView() == result
                if verbose:
                    print "Source:\n%s\nResult:\n%s" %(source, result)
                pass_count += 1
            except AssertionError:
                error_count += 1
                print (    "*** error ***\nSource:\n%s\nResult:\n%s\n\nExpected:\n%s\n"
                        %(source, r.treeView(), result) )
        # print summary
        print "\n*** Test suite: %s passed; %s failed ***" % (pass_count, error_count)
        return error_count

    def testSuiteDict(self, sources, method_name="parse", multiline = False):
        ''' Return & print a test dict for testSuite.
            Note that this should be done only once!
            Can also be used alone just to run and output
            test matches on a sequence of source expressions.
            '''
        # get proper match method
        method = getattr(self, method_name)
        # build & write out dict
        d = OrDict()
        for source in sources:
            try:
                result = method(source)
            except PijnuError:
                result = None
            d[source] = result
        # write dict out & return it
        # ~ Both source & result are written in repr format,
        #   so that reading back should yield correct objects.
        if multiline:
            i = 0
            sources = []
            results = []
            for (source, result) in d.items():
                print "source%s = \"\"\"%s\"\"\"" % (i, source)
                if result is not None:
                    result = result.treeView()
                print "result%s = \"\"\"%s\"\"\"" % (i, result)
                sources.append("source%s" % i)
                results.append("result%s" % i)
                i += 1
            print "sources = [", ', '.join(sources), "]"
            print "results = [", ', '.join(results), "]"
        else:
            print "test_suite_dict = {"
            for (source, result) in d.items():
                print "    \"%s\": \"%r\"" % (source, result.value)
            print "}"
        return d

    ### match check
    def _memoCheck(self, source, pos):
        ''' Wrapper func to implement packrat memoïzing algorithm.
            ~ Case check already done for this pos, use memo.
            ~ Else call _realCheck and memoize result.
        '''
        if Pattern.DO_STATS: Pattern.stats.trials += 1

        # case check result memoized for this position
        if pos in self.memo:
            if Pattern.DO_STATS: Pattern.stats.memos += 1
            result = self.memo[pos]
            # outcome was success
            r = result if isinstance(result,Node) else "*fail*"
            if isinstance(result,Node):
                return result
            # outcome was failure
            raise result

        # case not memoized yet
        if Pattern.DO_STATS: Pattern.stats.checks += 1
        try:
            result = self._realCheck(source, pos)
        except Invalidation, e:
            result = e
        self.memo[pos] = result
        # case success
        if isinstance(result,Node):
            if Pattern.DO_STATS:
                Pattern.stats.successes += 1
                if result.kind == Node.BRANCH:
                    Pattern.stats.branches += 1
                else:
                    Pattern.stats.leaves += 1
            return result
        # case failure
        if Pattern.DO_STATS:
            Pattern.stats.failures += 1
            if isinstance(result, Invalidation):
                Pattern.stats.invalids += 1
            elif isinstance(result, EndOfText):
                Pattern.stats.EOTs += 1
            else:
                Pattern.stats.matchFailures += 1
        raise result

    def _realCheck(self, source, pos):
        ''' Real match check when no memo available at current pos.
            ~ Outcome is either node or error.
            ~ New position in source is a node attribute.
        '''
        raise NotImplementedError

    def _message(self):
        ''' error message in case of failure
            * actually defined on each pattern type
            ~ used by errors together with view
        '''
        return "<match failure>"

    ### match actions
    def __call__(self, *actions):
        ''' Record transformations to be applied on node value.
            ~ () call is just used as a trick
            ~ transformations are only recorded in pattern
            ~ they will be processed at end of node init
        '''
        self.actions = actions
        return self

    ### output
    def _shortForm(self):
        ''' shorter output form for wrapped patterns:
            either name (if available), else format
        '''
        if self.name == Pattern.DEFAULT_NAME:
            # case from code: compute pattern's normal format
            if self.format is None: self.format = self._format()
            return self.format
        return self.name

    def _format(self):
        ''' normalized output format --defined on each pattern type
            ~ defined on first request for pattern output
            ~ patterns from text grammar keep original format
            ~ patterns from code get a computed normal form
        '''
        raise NotImplementedError

    def _fullFormat(self):
        ''' extensive output format, recursively including
            every sub pattern format (instead of names)
            ~ used when config FULL_OUTPUT is on
            * actually defined on each *wrapping* pattern type
        '''
        if self.format is None: self.format = self._format()
        return self.format

    def __str__(self):
        ''' standard output string "name:format"
        '''
        # case from code: compute pattern's normal format
        if self.format is None:
            self.format = self._format()
        if Pattern.FULL_OUTPUT:
            return "%s:%s" %(self.name,self._fullFormat())
        return "%s:%s" %(self.name,self.format)

    def _formatRepr(self):
        ''' representation of pattern creation syntax used by __repr__
            * defined on each pattern type
        '''
        raise NotImplementedError

    def __repr__(self):
        ''' representation of pattern creation syntax
            Example:
                Klass("0..9", name="digit")
                Choice([Word("foo"), word("bar")])
            * May be named or not.
            * Uses _formatRepr.
            * Recursive on wrapped patterns.
        '''
        typ = self.__class__.__name__
        args = self._formatRepr()
        if self.name == Pattern.DEFAULT_NAME:
            naming = ""
        else:
            naming = ', name="%s"' %self.name
        return '%s(%s%s)' %(typ,args,naming)


### literal word #############################
class Word(Pattern):
    ''' literal word pattern :   "word"
    '''
    def __init__(self, word, expression=None, name=None):
        ''' Define name, word, length, memo.'''
        self.word = word
        self.length = len(word)
        # define common attributes
        Pattern.__init__(self, expression, name)

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful if word is found at pos. '''
        startPos = pos
        end_pos = pos + self.length
        # case end of text
        if pos >= len(source):
            return EndOfText(self, source, pos)
        # case success
        if source[startPos:end_pos] == self.word:
            return Node(self, self.word, startPos,end_pos,source)
        # case failure
        return MatchFailure(self, source, pos)

    def _message(self):
        ''' error message in case of failure '''
        return """Cannot find word: "%s".""" % self.word

    def _format(self):
        ''' normal output format
        '''
        return '"%s"' % self.word

    def _formatRepr(self):
        ''' representation of pattern creation used by __repr__ '''
        return '"%s"' % self.word


### combinations #############################
class Choice(Pattern):
    ''' ordered choice pattern :    "a / b"
        Case repeted pattern is a Klass (or simple Char),
        a String pattern is yielded instead, via __new__
    '''
    def __new__(cls, patterns, expression=None, name=None):
        ''' Yield a Klass pattern if all patterns are either klasses or chars.
            Else yield standard Choice pattern.
        '''
        # Note: cls is Choice
        #
        # case patterns are Char-s or Klass-es
        if all( (isinstance(p,Klass) or isinstance(p,Char)) for p in patterns ):
            # compute data
            chars_sets = []
            for p in patterns:
                if isinstance(p,Klass):
                    chars_sets.append(p.charset)
                else:
                    chars_sets.append(p.char)
            charset = "".join(chars_sets)
            expressions = [p._format() for p in patterns]
            expression = "[%s]" % "/".join(expressions)
            # yield Klass pattern
            self = Klass(charset, expression,name)
            return self
        # else a Choice
        self = Pattern.__new__(cls, patterns, expression, name)
        return self

    def __init__(self, patterns, expression=None, name=None):
        ''' Define name, patterns, memo
        '''
        self.patterns = patterns
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = self.patterns    # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful iff one of sub patterns matches. '''
        startPos = pos
        sub_errors = []
        # try each sub pattern successively
        for pattern in self.patterns:
            # case success: keep information, apply nested pattern &
            # choice pattern transfos, avoid useless nesting.
            try:
                node = pattern._memoCheck(source, pos)
                # apply possible transformations stored on self
                # (in addition to the ones on wrapped pattern)
                if self.actions is not None:
                    node.doActions(self.actions)
                return node
            # case failure: collect error message used by _message
            # Note: This allows displaing while *each* pattern has failed.
            except PijnuError, e:
                e.wrap = True
                sub_errors.append(e)
        # case overall failure
        self.sub_errors = sub_errors
        return MatchFailure(self, source, pos)

    def _message(self):
        ''' error message in case of failure '''
        overall_message = ("Cannot match any pattern in choice.\n"
                        "(wrapped pattern errors below)")
        wrapped_message = '\n'.join(str(e) for e in self.sub_errors)
        return "%s\n%s" %(overall_message, wrapped_message)

    def _format(self):
        ''' normal output format
        '''
        pat_names = [p._shortForm() for p in self.patterns]
        return "(%s)" % ' / '.join(pat_names)

    def _fullFormat(self):
        ''' extensive output format
        '''
        pat_formats = [p._fullFormat() for p in self.patterns]
        return "(%s)" % ' / '.join(pat_formats)


class Sequence(Pattern):
    ''' ordered sequence pattern :   a b
    '''
    def __init__(self, patterns, expression=None, name=None):
        ''' Define name, patterns, memo.'''
        self.patterns = patterns
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = self.patterns    # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match in source string.
            ~ successful iff all patterns match in sequence. '''
        startPos = pos
        childNodes = Nodes()
        # try each sub pattern successively
        for pattern in self.patterns:
            # case success: append node to global value sequence
            try:
                node = pattern._memoCheck(source, pos)
                pos = node.end
                childNodes.append(node)
            # case failure:
            # record unsuccessful pattern error used by _message
            except PijnuError, e:
                e.wrap = True
                self.sub_error = e
                return MatchFailure(self, source, pos)
        # case overall success
        return Node(self, childNodes, startPos,pos,source)

    def _message(self):
        ''' error message in case of failure '''
        overall_message = ("Cannot match all patterns in sequence.\n"
                        "(wrapped pattern error below)")
        return "%s\n%s" % (overall_message,self.sub_error)

    def _format(self):
        ''' normal output format
        '''
        names = [p.name for p in self.patterns]
        pat_short_forms = [p._shortForm() for p in self.patterns]
        return "(%s)" % '  '.join(pat_short_forms)

    def _fullFormat(self):
        ''' extensive output format
        '''
        pat_formats = [p._fullFormat() for p in self.patterns]
        return "(%s)" % '  '.join(pat_formats)


### "possibilities" ##########################
class Option(Pattern):
    ''' option wrapper pattern :   p?
    '''
    def __init__(self, pattern, expression=None, name=None):
        ''' Define name, pattern, memo.'''
        self.pattern = pattern
        self.isOption = True
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = [self.pattern]   # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match in source string.
            ~ successful in all cases
            ~ returns nil node if wrapped pattern fails '''
        # Try matching wrapped pattern.
        # case success
        try:
            node = self.pattern._memoCheck(source, pos)
            # apply possible transformations stored on self
            # (in addition to the ones on wrapped pattern)
            if self.actions is not None:
                node.doActions(self.actions)
            return node
        # case failure: return nil node, pos does not move
        except PijnuError, e:
            return Node(self, Node.NIL, pos,pos,source)

    def _message(self):
        ''' ### option cannot fail! '''
        pass

    def _format(self):
        ''' normal output format
        '''
        return '%s?' % self.pattern._shortForm()

    def _fullFormat(self):
        ''' extensive output format
        '''
        return '(%s)?' % self.pattern._fullFormat()


class Next(Pattern):
    ''' positive lookahead pattern :   &p
    '''
    def __init__(self, pattern, expression=None, name=None):
        ''' Define name, pattern, memo.'''
        self.pattern = pattern
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = [self.pattern]   # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful if wrapped pattern succeeds. '''
        # Try matching wrapped pattern.
        # case success: keep pos unchanged and drop node value
        try:
            node = self.pattern._memoCheck(source, pos)
            return Node(self, Node.NIL, pos,pos,source)
        # case failure
        except PijnuError, e:
            e.wrap = True
            self.sub_error = e
            return MatchFailure(self, source, pos)

    def _message(self):
        ''' error message in case of failure '''
        overall_message = ( "Cannot match pattern:   %s.\n"
                            "(wrapped pattern error below)"
                            % self.pattern)
        return "%s\n%s" % (overall_message,self.sub_error)

    def _format(self):
        ''' normal output format
        '''
        return '&%s' % self.pattern._shortForm()

    def _fullFormat(self):
        ''' extensive output format
        '''
        return '&(%s)' % self.pattern._fullFormat()


class NextNot(Pattern):
    ''' negative lookahead pattern :   !p
    '''
    def __init__(self, pattern, expression=None, name=None):
        ''' Define name, pattern, memo.'''
        self.pattern = pattern
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = [self.pattern]   # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match in source string.
            ~ successful if wrapped pattern fails. '''
        # Try *NOT* matching wrapped pattern.
        # case "success": failure
        try:
            node = self.pattern._memoCheck(source, pos)
            return MatchFailure(self, source, pos)
        # case "failure": success
        # -- return nil node, keep pos unchanged
        except PijnuError, e:
            return Node(self, Node.NIL, pos,pos,source)

    def _message(self):
        ''' error message in case of failure '''
        # sub-pattern failure --> success:
        # ==> there is no sub-pattern error for NextNot!
        return "Found match for pattern:   %s." % self.pattern

    def _format(self):
        ''' normal output format
        '''
        return '!%s' % self.pattern._shortForm()

    def _fullFormat(self):
        ''' extensive output format
        '''
        return '!(%s)' % self.pattern._fullFormat()


### repetitions ##############################
### TODO: "Until" '>' stop condition
class ZeroOrMore(Pattern):
    ''' zero-or-more repetition pattern :   p*
    '''
    def __init__(self, pattern, expression=None, name=None):
        ''' Define name, pattern, memo.'''
        self.pattern = pattern
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = [self.pattern]   # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match in source string.
            ~ successful in all case
            ~ if wrapped pattern fails, returns nil node
            ~ else returns sequential "branch" node
            ~ node value is sequence of child nodes '''
        startPos = pos
        childNodes = Nodes()
        # Match wrapped pattern as many times as possible.
        while True:
            # case success: append node to child-sequence value
            try:
                node = self.pattern._memoCheck(source, pos)
                pos = node.end
                childNodes.append(node)
            # case failure: stop
            except PijnuError, e:
                break
        return Node(self, childNodes, startPos,pos,source)

    def _message(self):
        ''' ### zeroOrMore cannot fail! '''
        pass

    def _format(self):
        ''' normal output format
        '''
        return '%s*' % self.pattern._shortForm()


class OneOrMore(Pattern):
    ''' one-or-more repetition pattern : p+
    '''
    def __init__(self, pattern, expression=None, name=None):
        ''' Define name, pattern, memo.'''
        self.pattern = pattern
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = [self.pattern]   # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match in source string.
            ~ successful if wrapped pattern succeeds at least once
            ~ returns sequential "branch" node
            ~ node value is sequence of child nodes '''
        startPos = pos
        # First try matching wrapped pattern once.
        # case success go on
        try:
            node = self.pattern._memoCheck(source, pos)
            pos = node.end
            childNodes = Nodes(node)
        # case failure
        except PijnuError, e:
            e.wrap = True
            self.sub_error = e
            return MatchFailure(self, source ,pos)
        # Then match wrapped pattern as many times as possible.
        while True:
            # case success: append node to child sequence = value
            try:
                node = self.pattern._memoCheck(source, pos)
                pos = node.end
                childNodes.append(node)
            # case failure: stop
            except PijnuError, e:
                break
        return Node(self, childNodes, startPos,pos,source)

    def _message(self):
        ''' error message in case of failure '''
        overall_message = ( "Cannot match at all pattern:   %s.\n"
                            "(wrapped pattern error below)"
                            % self.pattern)
        return "%s\n%s" % (overall_message,self.sub_error)

    def _format(self):
        ''' normal output format
        '''
        return '%s+' % self.pattern._shortForm()


class Repetition(Pattern):
    ''' general repetition pattern
        Case repeted pattern is a Klass (or simple Char),
        a String pattern is yielded instead, via __new__

        Types of repetition suffix:
        ~ case numMin=numMax=False      <==> '*'
        ~ case numMin=1 & numMax=False  <==> '+'
        ~ case numMin=numMax >0         <==> {n}
        ~ general case numMin!=numMax   <==> {m..n}
        (see also _format())

        Note: numMax is max number, *not* an error condition.
        (if ever, an error will occur with next pattern anyway)
    '''
    def __new__(cls, pattern, numMin=False,numMax=False, expression=None, name=None):
        ''' Yield a String pattern if repeted pattern is a Klass or Char.
            Else yield standard Repetition pattern.
        '''
        # Note: cls is Repetition
        #
        # case pattern is Char: transform into Klass
        if isinstance(pattern,Char):
            (char,expression,name) = (  pattern.char,
                                        "[%s]" % pattern.char,
                                        pattern.name )
            pattern = Klass(char, expression,name)
        # case pattern is Klass: yield String instead
        # (contrary to the doc, no need to call __init__)
        if isinstance(pattern,Klass):
            self = String(pattern, numMin,numMax, expression,name)
            return self
        # else a Repetition
        self = Pattern.__new__(cls,pattern, numMin,numMax, expression,name)
        return self

    def __init__(self, pattern, numMin=False,numMax=False, expression=None, name=None):
        ''' Define name, pattern, memo, numMin & numMax.'''
        self.pattern = pattern
        # case '*':     numMin=False ; numMax=False
        # case '+':     numMin=1 ; numMax=False
        # case {m..}:   numMin=m ; numMax=False
        # case {n}:     numMin=numMax=n
        # case {m..n}:  numMin=m ; numMax=n
        if numMin==0: numMin = False
        if numMax==0: numMax = False
        self.numMin,self.numMax = numMin,numMax
        # define common attributes
        Pattern.__init__(self, expression, name)
        self.wrapped = [pattern]    # --> _resetMemo

    def _realCheck(self, source, pos):
        ''' Check pattern match in source string.
            ~ successful if wrapped pattern succeeds at least numMin time(s)
            ~ returns sequential "branch" node
            ~ node value is sequence of child nodes '''
        # Simply match as many times as possible
        # -- up to numMax if available, or up to failure.
        childNodes = Nodes()
        childNumber = 0
        startPos = pos
        numMax = self.numMax
        while True:
            # case success: append node to child sequence
            try:
                node = self.pattern._memoCheck(source, pos)
                pos = node.end
                childNodes.append(node)
                childNumber += 1
                # case numMax reached: stop
                if numMax and childNumber==numMax:
                    break
            # case failure: stop
            except PijnuError, e:
                e.wrap=True
                self.sub_error = e
                break
        # check numMin condition whenever
        if self.numMin and childNumber < self.numMin:
            return MatchFailure(self, source, pos)
        # result
        return Node(self, childNodes, startPos,pos,source)

    def _message(self):
        ''' error message in case of failure '''
        overall_message = ( "Cannot match at least %s time(s) pattern %s.\n"
                            "(wrapped pattern error below)"
                            % (self.numMin, self.pattern) )
        return "%s\n%s" % (overall_message,self.sub_error)

    def _format(self):
        ''' normal output format according to numMin/numMax case
        '''
        # if no max: '*' or '+' or {m..}
        if not self.numMax:
            if not self.numMin and not self.numMax:
                repete = '*'
            elif self.numMin == 1:
                repete = '+'
            else:
                repete = '{%s..}' %self.numMin
        # if max: {m..n} or {n}
        elif self.numMin==self.numMax:
            repete = "{%s}" % self.numMin
        else:
            repete = "{%s..%s}" % (self.numMin,self.numMax)
        return '%s%s' % (self.pattern._shortForm(),repete)


### character specific ##############
class Char(Pattern):
    ''' single char pattern :   'c'
    '''
    def __init__(self, char, expression=None, name=None):
        ''' Define name, char, memo.'''
        self.char = char
        # define common attributes
        Pattern.__init__(self, expression, name)

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful if char is found at pos. '''
        # case end of text
        if pos >= len(source):
            return EndOfText(self, source, pos)
        # case success
        if source[pos] == self.char:
            return Node(self, self.char, pos,pos+1,source)
        # case failure
        return MatchFailure(self, source, pos)

    def _message(self):
        ''' error message in case of failure '''
        return "Cannot find char: %s." % repr(self.char)

    def _format(self):
        ''' normal output format
        '''
        # rather return repr
        return repr(self.char)


class Klass(Pattern):
    ''' character class pattern :   [klass]
        ~ Expresses a choice among a set of chars.
        ~ Range is expressed using '..'.
        ~ '  ' can be used as separator for visual clarity.
        ~ May contain excluded characters after '!!':
            [a..z  A..Z  0..9  !!kq  B..Y  0] -->
            [abcdefghijlmnoprstuvwxyzAZ123456789]
        ~ Uses charset to parse charset expression
          and expand possible ranges inside it.
          --> see charset module for more info
    '''
    def __init__(self, format, expression=None, name=None):
        ''' Define name, format, charset, memo. '''
        # ~ From text grammar: format is an already computed charset.
        # ~ From source code: format is a klass format without brackets.
        #   In the latter case, we need to compute the charset
        #   using the toCharset tool func from module charset.
        #
        if expression is None:          # from code directly
            self.charset = toCharset(format)
            expression = "[%s]" % format
        else:                           # from text grammar
            self.charset = format
        # We need a clean text for format (see method _cleanRepr)
        expression = Klass._cleanRepr(expression)
        # define common attributes
        Pattern.__init__(self, expression, name)

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful if current char is in charset. '''
        # case end of text
        if pos >= len(source):
            return EndOfText(self, source, pos)
        # case success
        char = source[pos]
        
        # This way, Unicode characters, previously treated as bytes,
        # will pass; this is just a basic hack; a whole class allowing
        # ranges of characters would be far better.
        if char in self.charset or ord(char) > 255:
            return Node(self, char, pos, pos+1, source)
        # case failure
        return MatchFailure(self, source, pos)

    def _format(self):
        ''' normal output format
        '''
        # already computed by _cleanRepr(expression)
        return self.format

    def _message(self):
        ''' error message in case of failure '''
        return "Cannot find any char member of class %s." % self
    # tool func for clean text output
    control_chars = set( chr(n) for n in (range(0, 32) + range(127, 160)) )
    control_char_map = dict( (c, repr(c)[1:-1]) for c in control_chars )

    @staticmethod
    def _cleanRepr(text):
        ''' text with control chars replaced by repr() equivalent '''
        chars = ""
        for char in text:
            if char in ErrorLocation.control_chars:
                char = ErrorLocation.control_char_map[char]
            chars += char
        return chars


class String(Pattern):
    ''' character string pattern
        ~ Expresses a string of characters from a character klass,
          id est a klass repetition. (single char can be put in [])
        ~ Typical use: integer, name, text...
            name : [a..z]+   will yield a string pattern
        ~ Allows *, +, {m..} as well as {n} or {m,n} repetitions.
          !!! By default, numMin=1, which corresponds to '+'.
        ~ Possible "until" stop condition.
        * Note: unlike Repetition, default numMin is 1!
        * Note: numMax is *not* a failure case, a max char number instead.
        (failure will be detected by next pattern anyway)
    '''
    ''' "until" example:
        string  : [a..z  A..Z]+>"HALT"
            <=>
        string  : (!"HALT" [a..z  A..Z])+ "HALT"
    '''
    def __init__(self, klass, numMin=1,numMax=False, expression=None, name=None):
        ''' Define name, charsets, numMin,numMax, memo.'''
        # charsets used for checking
        self.charset = klass.charset
        self.klass = klass          # stored for output
        # case '*':     numMin=False ; numMax=False
        # case '+':     numMin=1 ; numMax=False
        # case {m..}:   numMin=m ; numMax=False
        # case {n}:     numMin=numMax=n
        # case {m..n}:  numMin=m ; numMax=n
        if numMin==0: numMin = False
        if numMax==0: numMax = False
        (self.numMin,self.numMax) = (numMin,numMax)
        # define common attributes
        Pattern.__init__(self, expression, name)
        # Note: no wrapped pattern (for _reset_memo),
        # cause we check the klass's charset directly.

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful if at least numMin number of
              chars --members of klass-- are found. '''
        # case end of text reached already
        if pos >= len(source):
            if self.numMin:
                # error
                return EndOfText(self, source, pos)
            return Node(self, Node.NIL, pos,pos,source)
        # Simply read as many valid chars as possible
        # -- up to numMax or end-of-text.
        startPos = pos
        # This is the position where to stop matching:
        if self.numMax and (startPos+self.numMax <= len(source)):
            stopPos = startPos + self.numMax
        else:
            stopPos = len(source)
        # looping
        charset = self.charset
        while (pos < stopPos) and (source[pos] in charset):
            pos += 1
        # result value:
        chars = source[startPos:pos]
        length = len(chars)
        # check numMin, case requested
        if (self.numMin) and (length < self.numMin):
            return MatchFailure(self, source, pos)
        # result:
        # possibly NIL
        if length == 0:
            node = Node(self, Node.NIL, pos,pos,source)
        node = Node(self, chars, startPos,pos,source)
        return node

    def _message(self):
        ''' error message in case of failure '''
        return "Cannot find minimal number of characters (%s)\n" \
                "members of class %s." % (self.numMin,self.klass)

    def _format(self):
        ''' normal output format
        '''
        # repetition
        if self.numMax:
            if self.numMin==self.numMax:
                repetition = "{%s}" % self.numMin
            else:
                repetition = "{%s..%s}" % (self.numMin,self.numMax)
        else:
            if self.numMin==False and self.numMax==False:
                repetition = "*"
            elif self.numMin==1 and self.numMax==False:
                repetition = "+"
            else:
                repetition = "{%s..}" % self.numMin
        # global output
        return "%s%s" % (self.klass._format(),repetition)


### "special" patterns ######################
class AnyChar(Pattern):
    ''' any char pattern :   .
        Actual matching depends on const KLASS
        ~ if none: AnyChar instance will really match any char
        ~ if is a class: AnyChar will match this class instead
          (intended to be the class of valid characters)
    '''
    KLASS = None

    def __init__(self, expression=None, name=None):
        ''' Define name, memo.'''
        if AnyChar.KLASS is not None:
            self.wrapped = [AnyChar.KLASS]  # --> _resetMemo
        # define common attributes
        Pattern.__init__(self, expression, name)

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ if KLASS is None: successful if not at end of source text.
            ~ else: check KLASS instead '''
        KLASS = AnyChar.KLASS
        # case no KLASS defined: match any char
        if KLASS is None:
            # case end of text
            if pos >= len(source):
                return EndOfText(self, source, pos)
            # case else: read current char
            return Node(self, source[pos], pos,pos+1,source)
        # case KLASS defined: match char in KLASS
        elif isinstance(KLASS,Klass):
            return KLASS._memoCheck(source, pos)
        # else error
        else:
            message = ( "AnyChar.KLASS should be a character class pattern.\n"
                        "Found %s:%s" %(KLASS.__class__.__name__,KLASS) )
            raise TypeError(message)

    def _message(self):
        ''' error message in case of failure '''
        return "Cannot find char: %s." % self.char

    def _format(self):
        ''' normal output format
        '''
        return "."

ANY_CHAR = AnyChar()


class Recursive(Pattern):
    ''' recursive pattern wrapper
        ~ only a trick to implement class recursivity
        ~ real pattern format is defined using '=='
        ~ see examples
    '''
    ''' examples
        x : ('a' x) / 'a'       <=>   x : 'a'+
        x       =  Recursive()
        x       == Sequence(Char('a'), x)

        x : '(' y ')' / 'a'
        x       =  Recursive()
        x       == Choice(Sequence('(' , y, ')'), 'a')

        group : '(' op ')'
        op  : (group / n) '*' (group / n)
        group   =  Recursive()
        op      = Sequence( Choice(group, n), Char(')'), Choice(group, n) )
        group   == Sequence( Char('('), op, Char(')') )

        mult  : (group / n) '*' (group / n)
        add   : (mult / n) '*' (mult / n)
        group : '(' (add / mult) ')'
        group   =  Recursive()
        mult    = Sequence( Choice(group, n), Char('*'), Choice(group, n) )
        add     = Sequence( Choice(mult, n), Char('+'), Choice(mult, n) )
        group   == Sequence( Char('('), Choice(add, mult), Char(')') )
    '''
    DEFAULT_FORMAT = "<recursive>"

    def __init__(self, expression=None, name=None):
        ''' A recursive pattern will actually be defined later
            using '**=' -- see __ipow__() method.
        '''
        Pattern.__init__(self, expression, name)
        self.isRecursive = True
        self.isDefined = False

    def __ipow__(self, pattern):
        ''' Record real definition of the pattern.
            ~ just a syntactic trick to cope with recursivity
        '''
        # Define common attributes, using wrapped pattern's format.
        (expression, name)  = (pattern.format, self.name)
        Pattern.__init__(self, expression, name)

        # Record wrapped pattern.
        self.pattern = pattern
        self.pattern.name = '@%s@' % self.name
        self.wrapped = [pattern]    # --> _resetMemo

        # Return self !!!
        self.isDefined = True
        return self

    def _realCheck(self, source, pos):
        ''' Check pattern match at position pos in source string.
            ~ successful if wrapped pattern is successful. '''
        if not self.isDefined:
            message = "Recursive pattern format undefined yet: %s" %self.name
            raise ValueError(message)
        # simply check through wrapped pattern
        try:
            node = self.pattern._memoCheck(source, pos)
            return node
        except PijnuError, e:
            e.pattern = self
            return e

    def _message(self):
        ''' error message in case of failure '''
        return "match failure for Recursive pattern %s" % self

    def _format(self):
        ''' normal output format
            -- actually wrapped pattern format
        '''
        if not self.isDefined:
            return Recursive.DEFAULT_FORMAT
        if self.pattern.format is None:
            self.pattern.format = self.pattern._format()
        return self.pattern.format

    def _shortForm(self):
        ''' short output form for recursive pattern:
            always fixed string to avoid infinite recursion '''
        if self.name == Pattern.DEFAULT_NAME:
            return Recursive.DEFAULT_FORMAT
        return self.name


class Clone(Pattern):
    ''' cloned pattern, to allow different match actions
        Special case of a pattern which definition happens
        to be the name of an original pattern:
        it will simply be cloned (deep-copied).
        One can than set match actions different from the original ones.
    '''
    def __new__(cls, pattern, expression=None, name=None):
        ''' Clone original pattern. '''
        self = clone(pattern)
        Pattern.__init__(self, expression, name)
        return self


### test #####################################
# in module testPattern
