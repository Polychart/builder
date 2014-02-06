###
This object should have all the metadata related to a metric.
Rather, this has all the objects that are true of a column, regarldess
of whether/how it is displayed
###
class ColumnInfo
  constructor: (dsInfo, params) ->
    {@name, @tableName} = dsInfo
    {@meta, @formula} = params
    @meta.tableName = @tableName
    # some derived types
    @gaType = if @meta.ga then "ga-#{@meta.ga}" else 'none'

  # Get the full formula for consumption by polyjs
  # - an ordinary column would return its full name, including the table name
  # - a derived column would go through its formula, replacing any identifiers
  #   and fully expand them recursively
  # - there is a check to ensure that we don't have an infinite recursion
  #
  # Note that this function returns an AST, a data structure that exists only
  # in polyjs. The returned structure should not be used without first calling
  # pretty() on it.
  #
  # should only be called from @getParsedFormula
  getParsedFormula: (tableMetaData, visited=[]) =>
    if not @formula
      if @name is 'count(*)'
        return polyjs.parser.parse("count(1)")
      else
        key = polyjs.parser.bracket("#{@tableName}.#{@name}")
        return polyjs.parser.parse(key)
    if _.has(visited, @name)
      throw Error "One of your formulas containing #{@name} is recursive!"
    visited.push @name
    expr = polyjs.parser.parse(@formula)
    visit = (name) =>
      ci = tableMetaData.getColumnInfo(name:name, tableName:@tableName)
      ci.getParsedFormula(tableMetaData, visited)

    if expr.name # top level is an identifier
      return visit(expr.name)

    visitor = {
      ident: (expr, name) ->       # shouldn't reach here
      const: (expr, val, type) ->  # shouldn't reach here
      call: (expr, fname, targs) ->
        for arg, i in expr.args
          if arg.name # it is an identifier
            expr.args[i] = visit(arg.name)
      infixop: (expr, opname, tlhs, trhs) ->
        for key in ['lhs', 'rhs']
          if expr[key].name
            expr[key] = visit(expr[key].name)
      conditional: (expr, tcond, tconseq, taltern) ->
        for key in ['condition', 'consequent', 'alternative']
          if expr[key].name
            expr[key] = visit(expr[key].name)
    }
    expr.visit(visitor)
    expr

  getFormula: (tableMetaData, unbracket=false) =>
    f = @getParsedFormula(tableMetaData).pretty()
    if unbracket
      polyjs.parser.unbracket f
    else
      f

module.exports = ColumnInfo
