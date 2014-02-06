# Top level view for viewing a particular chart
AbstractViewerEntryPoint = require('poly/main/main/viewer')
WorkspaceView            = require('poly/main/dash/workspace')

class DashViewerMainView extends AbstractViewerEntryPoint
  constructor: (@params) ->
    super(@params)

    tableMetaData = @dataView.getTableMetaData()
    @workspaceView = new WorkspaceView(@params.name, tableMetaData, true)
    @initialize()

  initialize: () ->
    initial = @params.initial ? []
    if _.isArray(@params.initial)
      initialItems = @params.initial
      initialCols = []
    else if _.isObject(@params.initial)
      initialItems = @params.initial.items ? []
      initialCols = @params.initial.newcols ? []

    @dataView.initialize initialCols, () => @workspaceView.initialize(initialItems)

module.exports = DashViewerMainView
