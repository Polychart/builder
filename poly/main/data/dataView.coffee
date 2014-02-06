Events              = require('poly/main/events')
TableMetricListView = require('poly/main/data/tableView')

TOAST               = require('poly/main/error/toast')

class DataView
  constructor: (@dataSource) ->
    @tables     = ko.observable({}) # obj where key=tableName, value=tableView
    @tableViews = ko.observableArray()

    Events.ui.table.focus.on (evt, info) =>
      {name} = info
      if name?
        @selectByName name

  initialize: (@initialCols=[], callback) =>
    @dataSource.listTables (err, result) =>
      if err
        console.error err
        TOAST.raise "An error occurred while listing tables"
        return
      @_doInitialize(result)
      callback() if callback

  _doInitialize: (newTables=[]) =>
    tables = @tables()
    first = true
    for tableName, tableData of newTables
      tables[tableName] = new TableMetricListView(tableData, @)
      tables[tableName].selected(first)
      first = false
    @tables(tables)
    @tableViews(_.values(tables))
    @addInitialCols()

  addInitialCols: () =>
    tables= @tables()
    for item in @initialCols
      tables[item.tableName].newDerivedMetric(null, item)
    @initialCols = []

  clearSelection: ->
    for t in @tableViews()
      t.selected no

  selectByName: (name) ->
    for t in @tableViews()
      t.selected(t.name is name)

  initTable: (domElements, tableView) ->
    tableView.afterRender(domElements[0])

  getColumnInfo: (dsInfo) =>
    tables = @tables()
    {tableName} = dsInfo
    # BEGIN: BACKWARD COMPATIBILITY FOR A GA TYPO
    if tableName is 'Vistor' and @dataSource.dsType is "googleAnalytics"
      tableName = 'Visitor'
    # END
    unless tableName and tables[tableName]?
      TOAST.raise("Table does not exist: #{tableName}")
      return
    tables[tableName].getColumnInfo(dsInfo)

  getTableMetaData: =>
    dsType:            @dataSource.dsType
    getDsKey:          @dataSource.dataSourceKey
    getTables:         () => _.keys @tables()
    getColumnsInTable: (tableName) =>
      _.without _.keys(@tables()[tableName].columnInfo), 'count(*)'
    getColumnInfo:     @getColumnInfo
    polyJsObjectFor:   @getPolyJsObject
    extendedMetaAsync: @getExtendedMetaAsync

  getPolyJsObject: (dsInfo) =>
    {tableName} = dsInfo
    # BEGIN: BACKWARD COMPATIBILITY FOR A GA TYPO
    if tableName is 'Vistor' and @dataSource.dsType is "googleAnalytics"
      tableName = 'Visitor'
    # END
    @tables()[tableName].jsdata

  getExtendedMetaAsync: (columnInfo, callback) =>
    {tableName, name, meta} = columnInfo
    # BEGIN: BACKWARD COMPATIBILITY FOR A GA TYPO
    if tableName is 'Vistor' and @dataSource.dsType is "googleAnalytics"
      tableName = 'Visitor'
    # END

    # TODO: Remove special case with GA
    gaMatch = /ga-(?:metric|dimension)-(.*)/.exec tableName
    if gaMatch then tableName = gaMatch[1]
    # end
    if meta.range
      callback null, meta
    else
      column =
        tableName: tableName
        name: name
        fullFormula: columnInfo.getFormula(@getTableMetaData(), false)
        derived: columnInfo.formula?
        type: meta.type
      @dataSource.getRange column, (err, result) =>
        if err
          callback err, null
        else
          meta.range = result
          if meta.type is 'cat'
            sortfn = polyjs.debug.type.compare('cat')
            meta.range.values = meta.range.values.sort sortfn
          callback null, meta

  serialize: () =>
    # serialize the derived columns
    _.flatten(t.serialize() for t in @tableViews())

module.exports = DataView
