import re
from decimal import Decimal

import pytest

from . import SCLLexer



data_numbers    = [ "1", "1.2", "+1.3", "-1.4", ".21", "+.22", "-.23" ]
data_scientific = [ "3e1", "+3E2", "-3E3", ".4E1", "+.4E1", "-.4E1", "+4.1E-7", "-4.1E+7", ]
data_strings    = [ r'string', r'string "quoted"', r'string (paren)', r'string ("paren quoted")' ]
data_keywords   = [ "keyword", "_keyword_", "123_hello" ]

def encode_number_key(value):    return "number="+value
def encode_number_value(value):  return [{ "key": "number", "value": Decimal(value) }]

def encode_keyword_key(value):   return "keyword="+value
def encode_keyword_value(value): return [{ "key": "keyword", "value": value }]

def encode_string_key(value):    return 'string="{quoted}"'.format(quoted=re.sub(r'(["()])', r'\\\1', value))
def encode_string_value(value):  return [{ "key": "string", "value": value }]



@pytest.fixture()
def lexer():
    return SCLLexer()


def test_constructor(lexer):
    assert lexer
    assert isinstance(lexer, SCLLexer)


@pytest.mark.parametrize('value', data_numbers )
def test_parse_numbers(lexer, value):
    input    = encode_number_key(value)
    expected = encode_number_value(value)
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data_scientific )
def test_parse_scientific(lexer, value):
    input    = encode_number_key(value)
    expected = encode_number_value(value)
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data_strings )
def test_parse_strings(lexer, value):
    input    = encode_string_key(value)
    expected = encode_string_value(value)
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data_keywords )
def test_parse_keywords(lexer, value):
    input    = encode_keyword_key(value)
    expected = encode_keyword_value(value)
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected
