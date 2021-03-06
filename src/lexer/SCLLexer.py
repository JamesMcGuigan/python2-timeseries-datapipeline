# Example:       https://www.dabeaz.com/ply/ply.html#ply_nn4
# Example:       https://www.dabeaz.com/ply/ply.html#ply_nn24
# Class example: http://www.dabeaz.com/ply/ply.html#ply_nn17

import re
from decimal import Decimal

import ply.lex as lex
import ply.yacc as yacc



class Lexer(object):
    defaults = {
        "debug": False,
        "optimize": 1,
        }
    tokens = ()
    names  = {}

    def __init__(self, *args, **kwargs):
        self.options = reduce(lambda a, b: dict(a, **b), [self.defaults] + list(args) + [kwargs])  # join arguments into single dict
        self.build()

    # Build the lexer
    def build(self, **kwargs):
        self.lexer  = lex.lex(module=self, **self.options)
        self.parser = yacc.yacc(module=self, **self.options )

    # Test it output
    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

    # Error handling rule
    def t_error(self,t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Error handling rule - http://www.dabeaz.com/ply/ply.html#ply_nn31
    def p_error(self, p):
        if p:
            print("Syntax error at token", p.type)
            # Just discard the token and tell the parser it's okay.
            self.parser.errok()
        else:
            print("Syntax error at EOF")


# TODO: Convert output format to: { "key1": (value, { children... }), "key2": (value) }
#       allowing for lookup as: result[key1][0] and result[key1][1][child_key2][0]
class SCLLexer(Lexer):

    ##### Lexer Rules #####

    # List of token names.   This is always required
    tokens = (
        'NUMBER',
        'STRING',
        'KEYWORD',
        'EQUALS',
        'LPAREN',
        'RPAREN',
        'WHITESPACE',
        'NEWLINE',
    )

    # Regular expression rules for simple tokens
    t_KEYWORD     = r'\w+'
    t_WHITESPACE  = r'[ ]+'
    t_EQUALS      = r'\s*=\s*'
    t_LPAREN      = r'[ ]*\([ ]*'
    t_RPAREN      = r'[ ]*\)'

    # A string containing ignored characters (spaces and tabs)
    # t_ignore  = ' \t'


    # A regular expression rule with some action code
    # Note addition of self parameter since we're in a class
    # Source: https://stackoverflow.com/questions/638565/parsing-scientific-notation-sensibly
    def t_NUMBER(self,t):
        r'[+-]?(\d*\.\d+|\d+)([eE][+-]?\d+)?\b'  # BUGFIX: \b ending required to avoid matching keyword 123_hello
        t.value = Decimal(t.value)
        return t

    # Source: https://stackoverflow.com/questions/249791/regex-for-quoted-string-with-escaping-quotes
    def t_STRING(self,t):
        r'"([^"\\]*(\\.[^"\\]*)*)"'
        t.value = re.sub(r'^"|"$', '',    t.value)
        t.value = re.sub(r'\\(.)', r'\1', t.value)
        return t

    # Define a rule so we can track line numbers
    def t_NEWLINE(self,t):
        r'([ ]*\n)+'
        t.lexer.lineno += len(t.value)



    ##### Parser Rules #####

    ### Parser Keywords
    # 'KEY',
    # 'VALUE',
    # 'PARENTHESES',
    # 'STATEMENT',
    # 'STATEMENTS',

    start = 'STATEMENTS'  # returned as: result = lexer.parser.parse(line)

    # FIXED: figure out how to create an accumulator for an array of values | requires: t_ignore  = '\s+'
    # NOTE:  "STATEMENT WHITESPACE STATEMENTS" produces same result as "STATEMENTS WHITESPACE STATEMENT"
    # NOTE:  STATEMENTS must match the entire line /^.*$/, hence must match all possible bounding whitespace possibilities
    # https://stackoverflow.com/questions/34445707/ply-yacc-pythonic-syntax-for-accumulating-list-of-comma-separated-values
    def p_STATEMENTS(self, p):
        '''
        STATEMENTS :            STATEMENT WHITESPACE STATEMENTS
                   | WHITESPACE STATEMENT WHITESPACE STATEMENTS
                   | WHITESPACE STATEMENT WHITESPACE STATEMENTS WHITESPACE 
                   | WHITESPACE STATEMENT
                   | WHITESPACE STATEMENT WHITESPACE
                   |            STATEMENT WHITESPACE
                   |            STATEMENT
        '''
        p[0] = []
        for n in range(1, len(p)):
            if isinstance(p[n], list): p[0] +=   p[n]
            if isinstance(p[n], dict): p[0] += [ p[n] ]


    def p_STATEMENT(self, p):
        '''
        STATEMENT : KEY EQUALS VALUE PARENTHESES
                  | KEY EQUALS PARENTHESES
                  | KEY EQUALS VALUE
        '''
        try:
            p[0] = { "key": p[1], "value": p[3], "children": p[4] }
        except:
            p[0] = { "key": p[1], "value": p[3] }

    
    def p_KEY(self, p):
        '''
        KEY     : KEYWORD
        '''
        p[0] = p[1]


    def p_VALUE(self, p):
        '''
        VALUE   : STRING
                | NUMBER
                | KEYWORD
        '''
        p[0] = p[1]


    def p_PARENTHESES(self, p):
        '''
        PARENTHESES : LPAREN STATEMENTS RPAREN
        '''
        p[0] = p[2]
