
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'STATEMENTSEQUALS KEYWORD LPAREN NEWLINE NUMBER RPAREN STRING WHITESPACE\n        STATEMENTS : STATEMENT WHITESPACE STATEMENTS\n                   | STATEMENT\n        \n        STATEMENT : KEY EQUALS VALUE PARENTHESES\n                  | KEY EQUALS PARENTHESES\n                  | KEY EQUALS VALUE\n        \n        KEY     : KEYWORD\n        \n        VALUE   : STRING\n                | NUMBER\n                | KEYWORD\n        \n        PARENTHESES : LPAREN STATEMENTS RPAREN\n        '
    
_lr_action_items = {'RPAREN':([3,7,8,9,10,11,12,14,15,16,],[-2,-1,-4,-7,-9,-8,-5,-3,16,-10,]),'WHITESPACE':([3,8,9,10,11,12,14,16,],[5,-4,-7,-9,-8,-5,-3,-10,]),'KEYWORD':([0,5,6,13,],[2,2,10,2,]),'EQUALS':([2,4,],[-6,6,]),'NUMBER':([6,],[11,]),'LPAREN':([6,9,10,11,12,],[13,-7,-9,-8,13,]),'STRING':([6,],[9,]),'$end':([1,3,7,8,9,10,11,12,14,16,],[0,-2,-1,-4,-7,-9,-8,-5,-3,-10,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'VALUE':([6,],[12,]),'PARENTHESES':([6,12,],[8,14,]),'STATEMENTS':([0,5,13,],[1,7,15,]),'KEY':([0,5,13,],[4,4,4,]),'STATEMENT':([0,5,13,],[3,3,3,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> STATEMENTS","S'",1,None,None,None),
  ('STATEMENTS -> STATEMENT WHITESPACE STATEMENTS','STATEMENTS',3,'p_STATEMENTS','SCLLexer.py',113),
  ('STATEMENTS -> STATEMENT','STATEMENTS',1,'p_STATEMENTS','SCLLexer.py',114),
  ('STATEMENT -> KEY EQUALS VALUE PARENTHESES','STATEMENT',4,'p_STATEMENT','SCLLexer.py',124),
  ('STATEMENT -> KEY EQUALS PARENTHESES','STATEMENT',3,'p_STATEMENT','SCLLexer.py',125),
  ('STATEMENT -> KEY EQUALS VALUE','STATEMENT',3,'p_STATEMENT','SCLLexer.py',126),
  ('KEY -> KEYWORD','KEY',1,'p_KEY','SCLLexer.py',136),
  ('VALUE -> STRING','VALUE',1,'p_VALUE','SCLLexer.py',143),
  ('VALUE -> NUMBER','VALUE',1,'p_VALUE','SCLLexer.py',144),
  ('VALUE -> KEYWORD','VALUE',1,'p_VALUE','SCLLexer.py',145),
  ('PARENTHESES -> LPAREN STATEMENTS RPAREN','PARENTHESES',3,'p_PARENTHESES','SCLLexer.py',152),
]
