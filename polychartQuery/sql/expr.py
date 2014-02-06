from polychartQuery.expr import ExprTreeVisitor
from polychartQuery.utils import isNumber

# GENERAL SHARED FUNCTIONS
QUOTE = "'" # note: double quote does not work in postgres!
def escape(str): return str # TODO: implement
def quote(str): return QUOTE+escape(str)+QUOTE
def unquote(str):
  if str[0] == QUOTE and str[-1] == QUOTE:
    return str[1:len(str)-1]
  return str
class ExprToSql(ExprTreeVisitor):
  def __init__(self):
    self.concat = "{0} ++ {1}"
    self.binnum = "ROUND({0}/{1}) * {1}"
    self.fns = {
      'log':    'LOG({0})'
      # string functions
    , 'length':  'CHAR_LENGTH({0})'
    , 'upper':  'UPPER({0})'
    , 'lower':  'LOWER({0})'
    , 'parseNum':  '0+{0}'
      # date functions

      # statistical aggregate functions
    , 'count':  'COUNT({0})'
    , 'mean':   'AVG({0})'
    , 'median': 'MEDIAN({0})'
    , 'max':    'MAX({0})'
    , 'min':    'MIN({0})'
    , 'sum':    'SUM({0})'
    , 'unique': 'COUNT(DISTINCT {0})'
      # for backend use only
    }
    self.binfns = {}
  def ident(self, name): return name # TODO: check for SQL Injection
  def const(self, type, value):
    if type == 'num':
      return value
    else:
      return quote(value)
  def infixop(self, opname, lhs, rhs):
    if opname in ["+", "-", "*", "/", "%", ">", "<", ">=", "<=", "!="]:
      return lhs + opname + rhs
    if opname == "==":
      return lhs + "=" + rhs
    if opname == "++":
      return self.concat.format(lhs, rhs)
    raise Exception("Unknown polyjs operation %s" % opname)
  def conditional(self, cond, conseq, altern):
    return "IF(%s, %s, %s)" % (cond, conseq, altern)
  def call(self, fname, args):
    if fname in self.fns:
      return self.fns[fname].format(*args)
    if fname == 'bin':
      return self.fn_bin(args)
    raise Exception("Unknown polyjs function %s" % fname)
  def fn_bin(self, args):
    key, bw = args
    if isNumber(bw):
      return self.binnum.format(key, bw)
    bw = unquote(bw)
    return self.binfns[bw].format(key)

class ExprToMySql(ExprToSql):
  def __init__(self):
    super(ExprToMySql, self).__init__()
    self.concat = "{0} ++ {1}"
    self.binnum = "ROUND({0}/{1}) * {1}"
    self.fns.update({
      # string functions
      'substr':  'SUBSTRING({0},{1}+1,{2})'
    , 'indexOf':  'INSTR({0},{1})-1'
      # date functions
    , 'year': 'YEAR({0})'
    , 'month': 'MONTH({0})'
    , 'dayOfMonth': 'DAY({0})'
    , 'dayOfYear': 'DAYOFYEAR({0})'
    , 'dayOfWeek': 'DAYOFWEEK({0})'
    , 'week': 'WEEK({0})'
    , 'hour': 'HOUR({0})'
    , 'minute': 'MINUTE({0})'
    , 'second': 'SECOND({0})'
      # for backend use only
    , 'unix':   'UNIX_TIMESTAMP({0})'
    })
    self.binfns.update({
      'second':   'UNIX_TIMESTAMP({0})'
    , 'minute':   'UNIX_TIMESTAMP(DATE_SUB({0},INTERVAL second({0}) SECOND))'
    , 'hour':     'UNIX_TIMESTAMP(DATE_SUB({0},INTERVAL 60*minute({0})+second({0}) SECOND))'
    , 'day':      'UNIX_TIMESTAMP(DATE({0}))'
    , 'week':     'UNIX_TIMESTAMP(DATE(SUBDATE({0},DAYOFWEEK({0})-1)))'
    , 'month':    'UNIX_TIMESTAMP(DATE(SUBDATE({0},DAYOFMONTH({0})-1)))'
    , 'twoMonth': "UNIX_TIMESTAMP(CONCAT(YEAR({0}),'-',MONTH({0})-MOD(MONTH({0}),2)+1,'-01'))"
    , 'quarter':  "UNIX_TIMESTAMP(CONCAT(YEAR({0}),'-',MONTH({0})-MOD(MONTH({0}),4)+1,'-01'))"
    , 'sixMonth': "UNIX_TIMESTAMP(CONCAT(YEAR({0}),'-',MONTH({0})-MOD(MONTH({0}),6)+1,'-01'))"
    , 'year':     'UNIX_TIMESTAMP(DATE(SUBDATE({0}, DAYOFYEAR({0})-1)))'
    , 'twoYear':  "UNIX_TIMESTAMP(CONCAT(YEAR({0}) - MOD(YEAR({0}), 2), '-01-01'))"
    , 'fiveYear': "UNIX_TIMESTAMP(CONCAT(YEAR({0}) - MOD(YEAR({0}), 5), '-01-01'))"
    , 'decade':   "UNIX_TIMESTAMP(CONCAT(YEAR({0}) - MOD(YEAR({0}), 10), '-01-01'))"
    })

exprToMySqlInstance = ExprToMySql()

def exprToMySql(expr):
  str = exprToMySqlInstance.visit(expr)
  if str == 'COUNT(1)':
    return 'COUNT(*)' # which one is faster?
  return str

class ExprToPostgres(ExprToSql):
  def __init__(self):
    super(ExprToPostgres, self).__init__()
    self.concat = "{0} || {1}"
    self.binnum = '({0}/{1})::int * {1}'
    self.fns.update({
      # string functions
      'substr':  'SUBSTRING({0} FROM {1}+1 FOR {2})'
    , 'indexOf':  'STRPOS({0}, {1})-1'
      # date functions
    , 'year': 'EXTRACT(YEAR FROM {0})'
    , 'month': 'EXTRACT(MONTH FROM {0})'
    , 'dayOfMonth': 'EXTRACT(DAY FROM {0})'
    , 'dayOfYear': 'EXTRACT(DOY FROM {0})'
    , 'dayOfWeek': 'EXTRACT(DOW FROM {0})'
    , 'week': 'EXTRACT(WEEK FROM {0})'
    , 'hour': 'EXTRACT(HOUR FROM {0})'
    , 'minute': 'EXTRACT(MINUTE FROM {0})'
    , 'second': 'EXTRACT(SECOND FROM {0})'
      # for backend use only
    , 'unix':   'EXTRACT(EPOCH FROM {0})'
    })
    self.binfns.update({
      'second':   'EXTRACT(EPOCH FROM {0})'
    , 'minute':   'EXTRACT(EPOCH FROM DATE_TRUNC(MINUTE, {0}))'
    , 'hour':     'EXTRACT(EPOCH FROM DATE_TRUNC(HOUR, {0}))'
    , 'day':      'EXTRACT(EPOCH FROM DATE_TRUNC(DAY, {0}))'
    , 'week':     'EXTRACT(EPOCH FROM DATE_TRUNC(WEEK, {0}))'
    , 'month':    'EXTRACT(EPOCH FROM DATE_TRUNC(MONTH, {0}))'
    , 'twoMonth': "EXTRACT(EPOCH FROM DATE_TRUNC(MONTH, {0}-(DATE_PART(MONTH,{0})::int%2||'MONTHS')::interval))"
    , 'quarter':  'EXTRACT(EPOCH FROM DATE_TRUNC(QUARTER, {0}))'
    , 'twoMonth': "EXTRACT(EPOCH FROM DATE_TRUNC(MONTH, {0}-(DATE_PART(MONTH,{0})::int%6||'MONTHS')::interval))"
    , 'year':     'EXTRACT(EPOCH FROM DATE_TRUNC(YEAR, {0}))'
    , 'twoYear':  "EXTRACT(EPOCH FROM DATE_TRUNC(YEAR, {0}-(DATE_PART(YEAR,{0})::int%2||'YEARS')::interval))"
    , 'fiveYear':  "EXTRACT(EPOCH FROM DATE_TRUNC(YEAR, {0}-(DATE_PART(YEAR,{0})::int%5||'YEARS')::interval))"
    , 'decade':    'EXTRACT(EPOCH FROM DATE_TRUNC(DECADE, {0}))'
    })
exprToPostgresInstance = ExprToPostgres()
def exprToPostgres(expr):
  str = exprToPostgresInstance.visit(expr)
  if str == 'COUNT(1)':
    return 'COUNT(*)' # which one is faster?
  return str
