# Top level view entry point - abstract classes
# Code that is shared for both chart and dashboard builder

Events      = require('poly/main/events')
DataView    = require('poly/main/data/dataView')
HeaderView  = require('poly/main/header')
OverlayView = require('poly/main/overlay')
ShareView   = require('poly/main/share')

class AbstractBuilderEntryPoint
  constructor: (@params) ->
    Events.registerDefaultListeners()

    {@dom, @dataCollection, @exportingEnabled} = params

    # TODO Support multiple data sources on client
    if @dataCollection
      unless _.isArray(@dataCollection)
        @dataCollection = [@dataCollection]
      @dataSource = poly.data @dataCollection[0]
      @dataView = new DataView(@dataSource)
      @overlayView = new OverlayView()
    else
      throw new Error('No data collection provided!')

    @hasHeader = params.header ? false
    @headerView = new HeaderView(params.isDemo)
    @shareView = new ShareView()

    if params.width is 'fill'
      $(@dom).width('100%')
    if _.isNumber(params.width)
      $(@dom).width(params.width)
    if params.height is 'fill'
      $(@dom).height('100%')
    if _.isNumber(params.height)
      $(@dom).height(params.height)
    if params.width is 'fill' and params.height is 'fill'
      $(@dom).addClass('fill')

  initialize: () =>
    @dataView.initialize()

module.exports = AbstractBuilderEntryPoint
