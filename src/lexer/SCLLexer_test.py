import re
from decimal import Decimal

import pytest

from . import SCLLexer



data = {
    "number":  [ "1", "1.2", "+1.3", "-1.4", ".21", "+.22", "-.23",
                 "3e1", "+3E2", "-3E3", ".4E1", "+.4E1", "-.4E1", "+4.1E-7", "-4.1E+7", ],
    "string":  [ r'string', r'string "quoted"', r'string (paren)', r'string ("paren quoted")' ],
    "keyword": [ "keyword", "_keyword_", "123_hello", "hello_123", "123_hello_123", "hello_123_world" ]
}
data_type_value_pairs = []
for type, values in data.items():
    for value in values:
        data_type_value_pairs.append( (type, value) )


def encode_input( value, type ):
    if type == "string":
        value = '"' + re.sub(r'(["()])', r'\\\1', value) + '"'
    return type+"="+value

def encode_output( value, type ):
    if type in ["number", "scientific"]:
        value = Decimal(value)
    return { "key": type, "value": value }

def encode_inputs_list( values, type ):
    return map(lambda value: encode_input(value, type), values)

def encode_inputs_string( values, type, join=" " ):
    return join.join( encode_inputs_list(values, type) )

def encode_outputs_list( values, type ):
    return map(lambda value: encode_output(value, type), values)



@pytest.fixture()
def lexer():
    return SCLLexer()


def test_constructor(lexer):
    assert lexer
    assert isinstance(lexer, SCLLexer)


@pytest.mark.parametrize('value', data['number'] )
def test_parse_numbers(lexer, value):
    input    = encode_input(value, 'number')
    expected = [encode_output(value, 'number')]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected


@pytest.mark.parametrize('value', data['string'] )
def test_parse_strings(lexer, value):
    input    = encode_input(value, 'string')
    expected = [ encode_output(value, 'string') ]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected


@pytest.mark.parametrize('value', data['keyword'] )
def test_parse_keywords(lexer, value):
    input    = encode_input(value, 'keyword')
    expected = [ encode_output(value, 'keyword') ]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected


@pytest.mark.parametrize('type', data.keys() )
def test_parse_statements_type(lexer, type):
    input    = encode_inputs_string( data[type], type )
    expected = encode_outputs_list(  data[type], type )
    actual   = lexer.parser.parse( input )
    assert   len(actual) == len(data[type])
    assert   actual == expected


def test_parse_statements_all(lexer):
    input    = ""
    expected = []
    for type in data.keys():
        input    += encode_inputs_string( data[type], type ) + " "
        expected += encode_outputs_list(  data[type], type )
    input    = input.strip()
    actual   = lexer.parser.parse( input )
    assert   len(actual) == sum(map(len, data.values()))
    assert   actual == expected


@pytest.mark.parametrize('whitespace', [ "%s", "  %s", "%s  ", "  %s  " ])
@pytest.mark.parametrize('type', data.keys() )
@pytest.mark.parametrize('size', [1, 2, 3] )
def test_parse_statements_whitespace(lexer, whitespace, type, size):
    # test for bounding whitespace combinations
    input    = encode_inputs_string( data[type][0:size], type, join=" "*size)
    input    = whitespace % (input)
    expected = encode_outputs_list(  data[type][0:size], type )
    actual   = lexer.parser.parse( input )
    assert   len(actual) == size
    assert   actual == expected


@pytest.mark.parametrize('whitespace', [ "%s", "  %s", "%s  ", "  %s  " ])
@pytest.mark.parametrize('type,value', data_type_value_pairs)
def test_parse_parentheses_single_single(lexer, type, value, whitespace):
    input    = [ "", encode_input(value, type), "(", encode_input(value, type), ")"]
    input    = "".join( map( lambda s: whitespace % s, input) )
    expected = [ encode_output(value, type) ]
    expected[0]['children'] = [ encode_output(value, type) ]
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected


@pytest.mark.parametrize('whitespace', [ "%s", "  %s", "%s  ", "  %s  " ])
@pytest.mark.parametrize('type', data.keys())
def test_parse_parentheses_single_multiple(lexer, whitespace, type):
    input    = [
            encode_input(data[type][0], type),
            "(",
            encode_inputs_string( data[type], type ),
            ")"
        ]
    input    = "".join( map( lambda s: whitespace % s, input) )
    expected = [ encode_output(data[type][0], type) ]
    expected[0]['children'] = encode_outputs_list( data[type], type )
    actual   = lexer.parser.parse( input )
    assert   len(actual) == 1
    assert   actual == expected


@pytest.mark.parametrize('size',     [1, 2, 3] )
@pytest.mark.parametrize('type',     data.keys() )
def test_parse_parentheses_multiple_single(lexer, type, size ):
    inputs   = encode_inputs_list(  data[type][0:size], type )
    expected = encode_outputs_list( data[type][0:size], type )

    for n in range(0, size):
        value   = data[type][n]
        inputs[n]              += "(" + encode_input(value, type) + ")"
        expected[n]["children"] =  [ encode_output(value, type) ]

    input  = " ".join(inputs)
    actual = lexer.parser.parse( input )
    assert len(actual) == size
    assert actual == expected
