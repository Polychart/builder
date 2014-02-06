# Top level view entry point - abstract classes
# Code that is shared for both chart and dashboard Viewer

DataView = require('poly/main/data/dataView')
Events   = require('poly/main/events')

class AbstractViewerEntryPoint
  constructor: (@params) ->
    Events.registerDefaultListeners()

    {@dom, @dataCollection} = params

    # TODO Support multiple data sources on client
    if @dataCollection
      unless _.isArray(@dataCollection)
        @dataCollection = [@dataCollection]
      # shared "views"
      @dataSource = poly.data @dataCollection[0]
    else
      throw new Error('No data collection provided!')

    @dataView = new DataView(@dataSource)

  initialize: () =>
    @dataView.initialize()

module.exports = AbstractViewerEntryPoint
