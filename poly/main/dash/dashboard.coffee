QuickAddView  = require('poly/main/dash/quickadd')
WorkspaceView = require('poly/main/dash/workspace')

class DashboardView
  constructor: (title, tableMetaData) ->
    @workspaceView = new WorkspaceView(title, tableMetaData)
    @quickaddView = new QuickAddView(tableMetaData)

  serialize: () =>
    @workspaceView.serialize()

  initialize: (initial) => @workspaceView.initialize(initial)

module.exports = DashboardView
