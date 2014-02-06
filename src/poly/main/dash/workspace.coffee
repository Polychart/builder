ChartItem      = require('poly/main/dash/item/chart')
CommentItem    = require('poly/main/dash/item/comment')
Events         = require('poly/main/events')
NumeralItem    = require('poly/main/dash/item/numeral')
PivotTableItem = require('poly/main/dash/item/pivottable')
TextItem       = require('poly/main/dash/item/text')

CONST          = require('poly/main/const')

class WorkspaceView
  workspace = null
  constructor: (@title, @tableMetaData, viewer = false) ->
    workspace = @

    unless ko.isObservable @title
      @title = ko.observable @title
    @items    = ko.observableArray()
    @gridSize = CONST.ui.grid_size
    @isViewer = ko.observable(viewer)

    @maxItemZIndex = ko.computed =>
      max = 0
      for item in @items()
        z   = item.zIndex() ? 0
        max = z if z > max
      max

    Events.ui.chart.add.on (event, params) =>
      params.itemType = "ChartItem"
      _.defer () =>
        @addItem(ItemFactory.makeItem(params, @tableMetaData))

    Events.ui.numeral.add.on (event, params) =>
      params.itemType = "NumeralItem"
      _.defer () =>
        @addItem(ItemFactory.makeItem(params, @tableMetaData))

    Events.ui.pivottable.add.on (event, params) =>
      params.itemType = "PivotTableItem"
      _.defer () =>
        @addItem(ItemFactory.makeItem(params, @tableMetaData))

    Events.ui.quickadd.add.on (event, params) =>
      _.defer () =>
        @addItem(ItemFactory.makeItem(params, @tableMetaData))

    Events.ui.dashboarditem.remove.on (event, params) =>
      {item} = params
      @removeItem(item)

    Events.ui.dashboarditem.select.on (event, params) =>
      {item} = params
      @shiftItems item.zIndex() ? 0
      item.zIndex @getNextZIndex()
      Events.model.dashboarditem.update.trigger()

    for type in ['svg', 'pdf', 'png']
      Events.export[type].click.on (evt, params) => params.callback @serialize()

  initialize: (initial) =>
    _.defer () =>
      _.each initial, (itemSpec) =>
        unless itemSpec.itemType is 'TitleItem'
          @addItem(ItemFactory.makeItem(itemSpec, @tableMetaData), true)

  getNextZIndex: =>
    @maxItemZIndex() + 1

  # decrements the z-index of all items whose z-index >= the parameter
  shiftItems: (minZ) =>
    for item in @items()
      z = item.zIndex() ? 0
      if z >= minZ
        item.zIndex z - 1

  getFreePosition: =>
    for x in [0..11]
      for y in [0..11]
        unless _.some(item.gridLeft() is x and item.gridTop() is y for item in @items())
          return left: x, top: y

  init: (@dom) =>

  serialize: () =>
    result = []

    for item in @items()
      serial = item.serialize()
      result.push(serial) if serial?

    return result

  addItem: (item, isDeserializing=false) =>
    unless isDeserializing
      item.zIndex(@getNextZIndex())

    @items.push(item)

    unless isDeserializing
      Events.model.dashboarditem.create.trigger()

  removeItem: (item) =>
    @items.remove(item)
    Events.model.dashboarditem.delete.trigger()

  class ItemFactory
    @ChartItem      = ->
      new ChartItem null, workspace.getFreePosition()
    @NumeralItem    = ->
      new NumeralItem workspace.getFreePosition()
    @PivotTableItem = ->
      new PivotTableItem workspace.getFreePosition()
    @TextItem       = ->
      new TextItem workspace.getFreePosition()
    @CommentItem    = ->
      new CommentItem null, null, workspace.getFreePosition()

    @makeItem: (serial, tableMetaData) =>
      if not serial.itemType then throw "Need to specify item type!"
      view = @[serial.itemType]()
      view.deserialize(serial)
      view.tableMetaData = tableMetaData
      view.isViewer workspace.isViewer()
      return view

module.exports = WorkspaceView
