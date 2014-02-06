Animation = require('poly/main/anim')
DashItem  = require('poly/main/dash/item/base')
Events    = require('poly/main/events')

CONST     = require('poly/main/const')
TOAST     = require('poly/main/error/toast')

PADDING = 10 # extra padding for chart view outside of chart

class PolyJSItem extends DashItem
  constructor: (@spec=null, position) ->
    @redraw = _.debounce(@_redraw, 300, true)
    @templateName = 'tmpl-chart-item' unless @templateName
    super(position)

  init: (dom) =>
    super(dom)
    @itemdom = $('.chart-inner, .inner', dom)
    @spec.dom = @itemdom[0]
    @_initSpec()
    Events.error.polyjs.data.on (event) =>
      @loadingAnim.stopOnImage("/static/main/images/broken_chart.svg")
    @onResize()

  _initSpec: () => Error("Not implemented")

  onResize: =>
    if @itemdom then @redraw()

  _redraw: () =>
   if !@itemdom
      # init() has to be called first so that @spec has a DOM element
      throw "Can't make chart before init() is called!"

    @spec.width = @itemdom.width() - PADDING
    @spec.height = @itemdom.height() - PADDING
    prepare =
      if @isViewer()
        ->
      else
        () => @itemdom.empty()
    @_renderPolyJSItem(@spec, @loaded, prepare)

  setSpec: (@spec, isDeserializing=false) =>
    unless isDeserializing
      Events.model.dashboarditem.update.trigger()

  deserialize: (s) =>
    @setSpec(s.spec, true)
    super(s)

module.exports = PolyJSItem
