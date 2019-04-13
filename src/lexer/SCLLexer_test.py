import re
from decimal import Decimal

import pytest

from . import SCLLexer



data_numbers    = [ "1", "1.2", "+1.3", "-1.4", ".21", "+.22", "-.23" ]
data_scientific = [ "3e1", "+3E2", "-3E3", ".4E1", "+.4E1", "-.4E1", "+4.1E-7", "-4.1E+7", ]
data_strings    = [ r'string', r'string "quoted"', r'string (paren)', r'string ("paren quoted")' ]
data_keywords   = [ "keyword", "_keyword_" ]

@pytest.fixture()
def lexer():
    return SCLLexer()


def test_constructor(lexer):
    assert lexer
    assert isinstance(lexer, SCLLexer)


@pytest.mark.parametrize('value', data_numbers )
def test_parse_numbers(lexer, value):
    input    = "number="+value
    expected = [{ "key": "number", "value": Decimal(value) }]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data_scientific )
def test_parse_scientific(lexer, value):
    input    = "scientific="+value
    expected = [{ "key": "scientific", "value": Decimal(value) }]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data_strings )
def test_parse_strings(lexer, value):
    quoted   = re.sub(r'(["()])', r'\\\1', value) 
    input    = 'string="{quoted}"'.format(quoted=quoted)
    expected = [{ "key": "string", "value": value }]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected

@pytest.mark.parametrize('value', data_keywords )
def test_parse_keywords(lexer, value):
    input    = "keyword="+value
    expected = [{ "key": "keyword", "value": value }]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected
