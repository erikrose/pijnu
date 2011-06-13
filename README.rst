`pijnu` is a PEG parser generator and processor, written in Python, intended to be clear, easy, practical.

`pijnu` was created in 2009 by Denis "Spir" Derman and then transferred to Peter Potrowl (peter17 on GitHub) in June 2011.

# Presentation
*See the wiki pages for details.*

## Syntax and grammar

`pijnu` syntax is a custom, extended version of Parsing Expression Grammars (PEG); which itself is a kind of mix of BNF and regular expressions.

The major difference is that PEG is a grammar to express string **recognition** patterns, while BNF or regexp express string **generation**. As a consequence, PEG is better suited for parsing tasks. A PEG grammar clearly encodes the *algorithm* to parse a source string, that simply needs to be rewritten into a parser coded in a programming language.

`pijnu` generated parsers use a library to parse source texts. This library mainly holds pattern classes, a Node type for the resulting parse tree, and several kinds of tool functions.

The parser is produced from the grammar by a generator which, indeed, itself "meta-uses" the library. For the story, all but the first generator were themselves "meta-produced" by previous versions of the generator: `pijnu` is *bootstrapped*.

    ### simple arithmetics with '+' and '*' only
    formula
    <definition>
    # tokens
    ADD        : '+'
    MULT       : '*'
    LPAREN     : '('
    RPAREN     : ')'
    digit      : [0..9.]
    number     : digit+
    # operations
    mult       : (grup/number) MULT (grup/mult/number)
    add        : (grup/mult/number) ADD (grup/add/mult/number)
    grup       : LPAREN (add / mult) RPAREN
    formula    : add / mult / number

## Post-process & transformations

A parsing phase produces a parse tree in which every node was yielded by a pattern. Simple leaf nodes hold the matched string snippet while branch nodes contain a sequence of child nodes. A major issue in text processing applications is that a raw parse tree is far from having a form well suited for further processing.

Using `pijnu`, one can do far more that getting a parse tree. The grammar allows assigning transformation functions to patterns, that will then be applied to every generated node. Numerous in-built transformations are provided in order to easily restructure the resulting parse tree and/or modify specific nodes.

Moreover, a user can write custom functions right inside the grammar that will then be applied to directly perform further processing. This is a both very simple and highly powerful method. In most cases, one can get final results "like magic".

For instance, to compute the actual result from the above *formula* grammar, one needs only 2 single-line functions: one for each operation indeed. Then, the result of the parsing/processing process *is* the result of the expressed formula.

Another example that will generate XHTML from wiki-text styled lines (possibly nested), using a single 3-lines function:

    ### parse wiki-text styled lines and rewrite them into XHTML
    wikInline
    <toolset>
    def styledSpan(node):
        klass = node.typ
        text = node.value
        node.value = '<span class="%s">%s</span>' %(klass,text)

    <definition>
    # codes
        ESCAPE         : '~'
        DISTINCT       : "//"                                : drop
        IMPORTANT      : "**"                                : drop
        styleCode      : (DISTINCT / IMPORTANT)
    # character expression
        escChar        : ESCAPE ('*' / '!' / '/' / ESCAPE)   : join
        validChar      : [\\x20..\\xff  !!/!*~]
        rawText        : (escChar / (!styleCode validChar))+ : join
    # text kinds
        distinctText   : DISTINCT inlineText DISTINCT        : liftValue
        importantText  : IMPORTANT inlineText IMPORTANT      : liftValue
        styledText     : distinctText / importantText        : styledSpan
        inlineText     : (styledText / rawText)+             : @ join

The column on right side assigns transformations to patterns. `drop`, `join`, and `liftValue` are builtin. `styledSpan` is a custom transformation. `'@'` denotes a recursive pattern.

## Practical use

*See the guide & tutorial in the wiki for details.*

As a tool, `pijnu` is hopefully clear and efficient for the user.

It provides highly informative feedback about patterns, results and exceptions.

Custom extensions from PEG help defining legible grammars -- there may be more in the future. There are also pre-processing functions and configuration parameters that may be worthful in practical cases, but still need be fully integrated.

Typically, a user will define the grammar, import the generator and let it write a corresponding parser. This parser comes in the form of a python module from which a parser object can be imported. The said parser object and each of its patterns can be used to match a source text partially or completely, find first or all occurrences of matches, or replace found matches. In most cases, transformation will restructure and further process the resulting parse tree.

    from pijnu import generator
    generator.writeParser(myGrammar)
    from myGrammarParser import myGrammarParser
    myGrammarParser.match(source)

It is also possible to directly produce a parser from the command line using the `gen.py` module (later may be renamed to `pijnu.py`):

    python gen.py myGrammar.pijnu myParser.py