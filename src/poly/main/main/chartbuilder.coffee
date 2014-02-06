# Top level view for Polychart Chart Builder (standalone)
AbstractBuilderEntryPoint = require('poly/main/main/builder')
ChartbuilderView          = require('poly/main/chart/chartbuilder')
DataTableView             = require('poly/main/data/datatableView')
Events                    = require('poly/main/events')

class ChartMainView extends AbstractBuilderEntryPoint
  constructor: (@params) ->
    @params.header = false # force there NOT to be a header, for now...
    super(@params)

    tableMetaData = @dataView.getTableMetaData()

    @chartbuilderView = new ChartbuilderView(tableMetaData)
    @chartbuilderVisible = ko.observable(true)
    @chartbuilderView.backButtonVisible(false)

    @dataTableView = new DataTableView(tableMetaData)
    @dataTableViewVisible = ko.observable(false)

    Events.nav.datatableviewer.open.on (event, params) => @loadDataviewer(params)
    Events.nav.datatableviewer.close.on (event, params) => @closeDataviewer(params)

    @initialize()

  initialize: () =>
    initial = @params.initial ? {}
    initialCols = initial.newcols ? []
    @dataView.initialize initialCols, () => @chartbuilderView.reset(spec: initial)

  loadDataviewer: (params={}) =>
    if not @dataTableViewVisible()
      params.previous = 'chart'
      @chartbuilderVisible(false)
    @dataTableViewVisible(true)
    @dataTableView.reset(params)

  closeDataviewer: (params) =>
    @dataTableViewVisible(false)
    @chartbuilderVisible(true)

  serialize: () => # PUBLIC FACING
    @chartbuilderView.serialize()

module.exports = ChartMainView
