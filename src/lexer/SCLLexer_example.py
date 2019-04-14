#!/usr/bin/env python2

import re
from os import path

import simplejson as json

from src.lexer.SCLLexer import SCLLexer



if __name__ == '__main__':
    ### Example: https://www.dabeaz.com/ply/ply.html#ply_nn4
    
    _filename = path.abspath(__file__)
    _dirname  = path.dirname(_filename)
    datafile = path.join( _dirname, 'SCL.txt' )

    with open(datafile) as file:
        data_lines = file.readlines()
        lexer  = SCLLexer()
        # for n in range(0,10000):  # optional loop for performance testing
        for linenumber, line in enumerate(data_lines):
            if not re.match(r'^\s*$', line):
                print "\n**********\n", linenumber, ':', line, "**********\n"

                if hasattr(lexer, 'lexer'):
                    lexer.lexer.input(line)
                    while True:
                        token = lexer.lexer.token()
                        if not token: break # No more input
                        print token

                if hasattr(lexer, 'parser'):
                    result = lexer.parser.parse(line)
                    print "***** result *****: "
                    print json.dumps(result, indent=4*' ')
