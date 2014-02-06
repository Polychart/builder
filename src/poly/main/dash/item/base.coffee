Animation = require('poly/main/anim')
Events    = require('poly/main/events')

CONST     = require('poly/main/const')
TOAST     = require('poly/main/error/toast')

class DashItem
  constructor: (pos) ->
    unless @templateName
      throw "DashItem must have a template name before super constructor is called"

    @error = ko.observable null

    @isViewer = ko.observable false
    @zIndex = ko.observable 0

    @gridSize = CONST.ui.grid_size

    # allow child classes to override
    @minWidth or= 2
    @minHeight or= 2

    @gridTop = ko.observable 0
    @gridLeft = ko.observable 0
    @gridWidth = ko.observable 0
    @gridHeight = ko.observable 0

    @size = ko.computed
      read: =>
        width: @gridWidth()
        height: @gridHeight()
      write: (val={}) =>
        {width, height} = val
        (@gridWidth Math.max width, @minWidth) if width?
        (@gridHeight Math.max height, @minHeight) if height?
    @position = ko.computed
      read: =>
        _.extend @size(), {
          top: @gridTop()
          left: @gridLeft()
        }
      write: (val={}) =>
        @size val
        {top, left} = val
        (@gridTop Math.max top, 0) if top?
        (@gridLeft Math.max left, 0) if left?

    @position pos

    @size.subscribe (val) =>
      @onResize val
    @_posSub = @position.subscribe ->
      Events.model.dashboarditem.update.trigger()

    @isDragging = ko.observable false
    @isResizing = ko.observable false

    interactive = ko.computed =>
      not @isViewer()

    @dragResizeParams = {
      @gridSize,
      @minWidth, @minHeight,
      @gridTop, @gridLeft, @gridWidth, @gridHeight,
      @isDragging, @isResizing,
      dragEnabled: interactive, resizeEnabled: interactive
    }

  init: (@dom) =>
    @loadingAnim = new Animation('loading', @dom)

  loaded: (err) =>
    if err
      console.error err
      @error err.message
      @loadingAnim.stopOnImage("/static/main/images/broken_chart.svg")
    else
      @loadingAnim.remove()
      @error null

  onSelect: (item, event) =>
    Events.ui.dashboarditem.select.trigger item: item
    return true

  # may be overridden
  onResize: ->

  deleteItem: () =>
    Events.ui.dashboarditem.remove.trigger item: @

  serialize: (s) =>
    unless s.itemType
      throw new Error('DashItem subclass must specify itemType')

    s.position = @position()
    s.zIndex = @zIndex()
    return s

  deserialize: (s) =>
    # Otherwise _save will be invoked and the last item to be deserialized will
    # be forgotten if no other update events are fired.
    if s?.position
      @_posSub.dispose()
      @position s?.position
      @_posSub = @position.subscribe ->
        Events.model.dashboarditem.update.trigger()
    @zIndex s?.zIndex

module.exports = DashItem
