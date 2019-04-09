#!/usr/bin/env python2
### Example: https://www.dabeaz.com/ply/ply.html#ply_nn4

import re
from os import path

import simplejson as json

from src.lexer.SCLLexer import SCLLexer  # , SLCParser

_filename = path.abspath(__file__)
_dirname  = path.dirname(_filename)
datafile = path.join( _dirname, 'SCL.txt' )

with open(datafile) as file:
    data_string = file.read()
with open(datafile) as file:
    data_lines = file.readlines()

for name, data in { "string": [data_string], "lines": data_lines }.iteritems():

    lexer  = SCLLexer()

    for linenumber, line in enumerate(data):
        if not re.match(r'^\s*$', line):
            print "\n**********\n", name, ':', linenumber, ':', line, "**********\n"

            if hasattr(lexer, 'lexer'):
                lexer.lexer.input(line)
                while True:
                    token = lexer.lexer.token()
                    if not token: break # No more input
                    print token

            if hasattr(lexer, 'parser'):
                result = lexer.parser.parse(line)
                while True:
                    token = lexer.parser.token()
                    if not token or token.type == 'SEMI': break
                    print token
                print "***** result *****: "
                print json.dumps(result, indent=4*' ')
