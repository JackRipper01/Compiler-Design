
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'leftPLUSMINUSleftTIMESDIVIDErightLPARENRPARENnonassocUMINUSDIVIDE LPAREN MINUS NUMBER PLUS RPAREN TIMESstatement : expressionexpression : NUMBERexpression : MINUS expression %prec UMINUSexpression : LPAREN expression RPARENexpression : expression PLUS expression\n    | expression MINUS expression\n    | expression TIMES expression\n    | expression DIVIDE expression'
    
_lr_action_items = {'NUMBER':([0,4,5,6,7,8,9,],[3,3,3,3,3,3,3,]),'MINUS':([0,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,],[4,7,-2,4,4,4,4,4,4,-3,7,-5,-6,-7,-8,-4,]),'LPAREN':([0,4,5,6,7,8,9,],[5,5,5,5,5,5,5,]),'$end':([1,2,3,10,12,13,14,15,16,],[0,-1,-2,-3,-5,-6,-7,-8,-4,]),'PLUS':([2,3,10,11,12,13,14,15,16,],[6,-2,-3,6,-5,-6,-7,-8,-4,]),'TIMES':([2,3,10,11,12,13,14,15,16,],[8,-2,-3,8,8,8,-7,-8,-4,]),'DIVIDE':([2,3,10,11,12,13,14,15,16,],[9,-2,-3,9,9,9,-7,-8,-4,]),'RPAREN':([3,10,11,12,13,14,15,16,],[-2,-3,16,-5,-6,-7,-8,-4,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'statement':([0,],[1,]),'expression':([0,4,5,6,7,8,9,],[2,10,11,12,13,14,15,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> statement","S'",1,None,None,None),
  ('statement -> expression','statement',1,'p_statement_expr','ast_inventing.py',141),
  ('expression -> NUMBER','expression',1,'p_expression_number','ast_inventing.py',146),
  ('expression -> MINUS expression','expression',2,'p_expression_uminus','ast_inventing.py',159),
  ('expression -> LPAREN expression RPAREN','expression',3,'p_expression_group','ast_inventing.py',164),
  ('expression -> expression PLUS expression','expression',3,'p_expression_binop','ast_inventing.py',170),
  ('expression -> expression MINUS expression','expression',3,'p_expression_binop','ast_inventing.py',171),
  ('expression -> expression TIMES expression','expression',3,'p_expression_binop','ast_inventing.py',172),
  ('expression -> expression DIVIDE expression','expression',3,'p_expression_binop','ast_inventing.py',173),
]
