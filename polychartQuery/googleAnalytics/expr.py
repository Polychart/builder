from polychartQuery.expr import ExprTreeVisitor

QUOTE = "'" # note: double quote does not work in postgres!
def escape(str): return str # TODO: implement
def quote(str): return QUOTE+escape(str)+QUOTE
def unquote(str):
  if str[0] == QUOTE and str[-1] == QUOTE:
    return str[1:len(str)-1]
  return str

class ExprToGA(ExprTreeVisitor):
  def __init__(self):
    self.fns = {
    }
    self.binfns = {
      'hour':      'date,ga:hour'
    , 'day':       'date'
    , 'week':      'date,ga:week'
    , 'month':     'month,ga:year'
    , 'twomonth':  'month,ga:year'
    , 'quarter':   'month,ga:year'
    , 'sixmonth':  'month,ga:year'
    , 'year':      'year'
    , 'twoyear':   'year'
    , 'fiveyear':  'year'
    , 'decade':    'year'
    }
  def ident(self, name): return name
  def const(self, type, value):
    if type == 'num':
      return value
    else:
      return quote(value)
  def infixop(self, opname, lhs, rhs):
    raise Exception("Unsupported operation %s" % opname)
  def conditional(self, cond, conseq, altern):
    raise Exception("Unsupported operation: conditionals.")
  def call(self, fname, args):
    if fname == 'bin':
      return self.fn_bin(args)
    return args[0]
  def fn_bin(self, args):
    key, bw = args
    bw = unquote(bw)
    if bw in self.binfns:
      return self.binfns[bw]
    else:
      return key

exprToGAInstance = ExprToGA()
def exprToGA(expr):
  str = exprToGAInstance.visit(expr)
  if str == 'COUNT(1)':
    return 'COUNT()' # which one is faster?
  return str
