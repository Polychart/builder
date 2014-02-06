class MetricView
  constructor: (@columnInfo) ->
    {@name, @tableName, @gaType} = @columnInfo
    @type = @columnInfo.meta.type
    @gaType = @columnInfo.gaType
    @originalFormula = @columnInfo.formula
    @formula =
      if @originalFormula?
        @originalFormula
      else if @name == 'count(*)'
        @name
      else
        "[#{@tableName}.#{@name}]"
    @extraCSS =
      if @columnInfo.formula
        'derived-var'
      else
        @gaType

  fullFormula: (tableMetaData, unbracket=false) =>
    @columnInfo.getFormula(tableMetaData, unbracket)

  fullMeta: () -> @columnInfo.meta

module.exports = MetricView
