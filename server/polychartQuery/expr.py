"""
Abstract expression related helper functions
"""

class ExprTreeVisitor(object):
  """
  Abstract expression tree visitor for performing arbitrary tasks with a
  PolyJS expression tree
  """
  def visit(self, ast):
    tag, fields = ast
    fn = getattr(self, '_' + tag)
    return fn(fields)
  def _mapVisit(self, fields, *names):
    return [self.visit(fields[name]) for name in names]
  def _ident(self, fields): return self.ident(fields['name'])
  def _const(self, fields): return self.const(fields['type'], fields['value'])
  def _infixop(self, fields):
    visited = self._mapVisit(fields, 'lhs', 'rhs')
    return self.infixop(fields['opname'], *visited)
  def _conditional(self, fields):
    visited = self._mapVisit(fields, 'cond', 'conseq', 'altern')
    return self.conditional(*visited)
  def _call(self, fields):
    args = [self.visit(arg) for arg in fields['args']]
    return self.call(fields['fname'], args)

def exprCallFnc(fname, args):
  return ['call', {'fname': fname, 'args': args}]

class Validator(ExprTreeVisitor):
  def __init__(self, columns):
    self.columns = columns
  def ident(self, name):
    return name in self.columns
  def const(self, type, value):
    return True
  def infixop(self, opname, lhs, rhs):
    return lhs and rhs
  def conditional(self, cond, conseq, altern):
    return cond and conseq and altern
  def call(self, fname, args):
    return all(args)

def getExprValidator(columns):
  """
  Returns a function that verifies that identifiers exist in the
  given list of identifiers `columns`.
  This is mainly to protect against SQL injection attacks.

  Args:
    columns: A list of acceptable identifiers

  Returns:
    Function that throws a ValueError when encountering bad input
  """
  v = Validator(columns)
  def validate(obj):
    expr = obj['expr']
    name = obj['name']
    if not v.visit(expr):
      raise ValueError("Unknown data column %s" % name)
  return validate
