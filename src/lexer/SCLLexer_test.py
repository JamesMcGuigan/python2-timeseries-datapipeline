import re
from decimal import Decimal

import pytest

from . import SCLLexer



data = {
    "number":  [ "1", "1.2", "+1.3", "-1.4", ".21", "+.22", "-.23",
                 "3e1", "+3E2", "-3E3", ".4E1", "+.4E1", "-.4E1", "+4.1E-7", "-4.1E+7", ],
    "string":  [ r'string', r'string "quoted"', r'string (paren)', r'string ("paren quoted")' ],
    "keyword": [ "keyword", "_keyword_", "123_hello", "hello_123" ]       
}

def encode_key(value, type):
    if type == "string":
        value = '"' + re.sub(r'(["()])', r'\\\1', value) + '"'
    return type+"="+value

def encode_value(value, type):
    if type in ["number", "scientific"]:
        value = Decimal(value)
    return { "key": type, "value": value }
    
    
@pytest.fixture()
def lexer():
    return SCLLexer()


def test_constructor(lexer):
    assert lexer
    assert isinstance(lexer, SCLLexer)


@pytest.mark.parametrize('value', data['number'] )
def test_parse_numbers(lexer, value):
    input    = encode_key( value, 'number' )
    expected = [ encode_value( value, 'number' ) ]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data['string'] )
def test_parse_strings(lexer, value):
    input    = encode_key( value, 'string' )
    expected = [ encode_value( value, 'string' ) ]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data['keyword'] )
def test_parse_keywords(lexer, value):
    input    = encode_key( value, 'keyword' )
    expected = [ encode_value( value, 'keyword' ) ]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected


@pytest.mark.parametrize('type', data.keys() )
def test_parse_statements_type(lexer, type):
    input    = " ".join( map(lambda value: encode_key(value, type), data[type]) )
    expected = map(lambda value: encode_value(value, type), data[type])
    actual   = lexer.parser.parse( input )
    assert   len(actual) == len(data[type])
    assert   actual == expected

def test_parse_statements_all(lexer):
    input    = ""
    expected = []
    for type in data.keys():
        input    += " ".join( map(lambda value: encode_key(value, type), data[type]) ) + " "
        expected += map(lambda value: encode_value(value, type), data[type])
    input    = input.strip()
    actual   = lexer.parser.parse( input )
    assert   len(actual) == sum(map(len, data.values()))
    assert   actual == expected

@pytest.mark.parametrize('format', [ "%s", "  %s", "%s  ", "  %s  " ])
@pytest.mark.parametrize('type', data.keys() )
@pytest.mark.parametrize('size', [1, 2, 3] )
def test_parse_statements_whitespace(lexer, format, type, size):
    # test for bounding whitespace combinations
    input    = (" " * size).join( map(lambda value: encode_key(value, type), data[type][0:size]) )
    input    = format % (input)
    expected = map(lambda value: encode_value(value, type), data[type][0:size])
    actual   = lexer.parser.parse( input )
    assert   len(actual) == size
    assert   actual == expected
