Events                  = require('poly/main/events')
QuickAddAesthetic       = require('poly/main/dash/aes')
QuickAddTableMetricView = require('poly/main/data/metric/quickaddtable')
{JoinsView}             = require('poly/main/chart/joins')

CONST                   = require('poly/main/const')
DND                     = require('poly/main/dnd')
TOAST                   = require('poly/main/error/toast')

class QuickAddView
  constructor: (tableMetaData) ->
    @lineView = new QuickAddLineItemView
      name: 'Line Chart'
      img: 'line'
      aes1: 'X Axis'
      aes2: 'Y Axis'
      tableMetaData: tableMetaData
    Events.ui.quickadd.expand.onElem @lineView, @clearOther
    @barView = new QuickAddBarItemView
      name: 'Bar Chart'
      img: 'bar'
      aes1: 'X Axis'
      aes2: 'Y Axis'
      tableMetaData: tableMetaData
    Events.ui.quickadd.expand.onElem @barView, @clearOther
    @pieView = new QuickAddPieItemView
      name: 'Pie Chart'
      img: 'pie'
      aes1: 'Categories'
      aes2: 'Values'
      tableMetaData: tableMetaData
    Events.ui.quickadd.expand.onElem @pieView, @clearOther
    @commentView = new QuickAddCommentView
      name: 'Annotation'
      img: 'annotation'

    @numeralView = new QuickAddNumeralView
      tableMetaData: tableMetaData
    @tableView = new QuickAddTableView
      tableMetaData: tableMetaData

  clearOther: (event, params) =>
    {elem} = params
    for item in [@lineView, @barView, @pieView, @numeralView]
      if item isnt elem
        item.expanded(false)
  initQuickAddItem: (domElements, view) ->
    view.afterRender(domElements[0])
  newCustomChart: () =>
    Events.ui.quickadd.click.trigger info: name: "Custom"
    Events.nav.chartbuilder.open.trigger()
  newCustomTable: () =>
    Events.ui.quickadd.click.trigger info: name: "CustomTable"
    Events.nav.tablebuilder.open.trigger()

class AbstractQuickAdd
  constructor: () ->
  addItem: () => throw "Need to be defined"


class AbstractExpandableQuickAdd extends AbstractQuickAdd
  constructor: (params) ->
    super(params)
    {@tableMetaData} = params
    @successIndicatorVisible = ko.observable(false)
    @expanded = ko.observable(false)
    @expanded.subscribe (isExpanded) =>
      if isExpanded # Clear immediately if expanding
        Events.ui.quickadd.expand.trigger info: name: @name
        @onExpand()
      unless isExpanded
        Events.ui.quickadd.collapse.trigger info: name: @name
        @onCollapse()
        setTimeout =>
          @successIndicatorVisible(false)
        , 500
    @maxHeight = ko.observable(0)
    @renderHeight = ko.computed =>
      if @expanded()
        @maxHeight()
      else
        0
  onExpand: () => throw "Need to be defined"
  onCollapse: () => throw "Need to be defined"
  toggleExpand: (view, event) =>
    @expanded(!@expanded())
    Events.ui.quickadd.expand.triggerElem @, elem: @
    @_recalculateExpansion(event.target)
  collapse: () =>
    @expanded(false)
    Events.ui.dropdown.enable.trigger()
  _recalculateExpansion: (domElementInView) ->
    # Find appropriate element
    if $(domElementInView).hasClass('quickadd-container')
      expansion = $(domElementInView).find('.expansion')
    else
      expansion =
        $(domElementInView).parents('.quickadd-container').find('.expansion')
    # Match max-height to height of contents
    @maxHeight expansion.children().outerHeight()
  _makeMeta: (aeses) =>
    meta = {}
    for aes in aeses
      meta[aes.fullFormula(@tableMetaData, true)] = _.extend aes.fullMeta(), {
        tableName: aes.tableName,
        dsKey: @tableMetaData.dsKey
      }
    meta

class QuickAddItemView extends AbstractExpandableQuickAdd
  constructor: (params) ->
    super(params)
    {@name, @img, @aes1, @aes2, @tableMetaData} = params
    @imageClass = "large-icon img-icon-" + @img
    @metricView1 = new QuickAddAesthetic(@, @aes1, @options1, @tableMetaData)
    @metricView2 = new QuickAddAesthetic(@, @aes2, @options2, @tableMetaData)
    @joinsView = new JoinsView(@tableMetaData, {}, @)
    @attachedMetrics = ko.computed () =>
      _.compact [@metricView1.metric(), @metricView2.metric()]
  checkNewMetric: (event, item, callback) =>
    @joinsView.checkAddJoins(event, item, callback)
  checkRemoveMetric: (event, item) =>
    @joinsView.checkRemoveJoins()
  onExpand: () =>
    @metricView1.clear()
    @metricView2.clear()
    @joinsView.reset()
  onCollapse: () =>
    @metricView1.disable()
    @metricView2.disable()
  addItem: () =>
    if @metricView1.metric() and @metricView2.metric()
      # TODO: Get rid of terrible hack.
      [m1, m2] = [@metricView1.metric(), @metricView2.metric()]
      if m1.gaType isnt 'none' and m2.gaType isnt 'none' and 'ga-metric' not in [m1.gaType, m2.gaType]
        TOAST.raise "Google Analytics charts require at least one metric—orange—item!"
      else
        @_addItem (success) =>
          if success
            @successIndicatorVisible(true)
            Events.ui.dropdown.disable.trigger()
            @metricView1.disable()
            @metricView2.disable()
            setTimeout @collapse, 2000
  _addItem: () =>
    Events.ui.chart.add.trigger spec: null

class QuickAddLineItemView extends QuickAddItemView
  options1: () => CONST.layers.line.x
  options2: () => CONST.layers.line.y
  _addItem: (callback) =>
    x = @metricView1.metric()
    y = @metricView2.metric()
    layer =
      meta: @_makeMeta [x, y]
      type: 'line'
      x: x.generateSpec(@tableMetaData)
      y: y.generateSpec(@tableMetaData)
      additionalInfo:
        joins: @joinsView.generateSpec()
    Events.ui.chart.add.trigger
      spec:
        layer: layer
    callback(true)

class QuickAddBarItemView extends QuickAddItemView
  constructor: (params) ->
    super(params)
    @metricView2.dropFilter = (dom) ->
      $(dom).data('dnd-data').meta.type in ['date', 'num']
  options1: () => CONST.layers.bar.x
  options2: () => CONST.layers.bar.y
  _addItem: (callback) =>
    x = @metricView1.metric()
    y = @metricView2.metric()
    layer =
      type: 'bar'
      meta: @_makeMeta [x, y]
      x: x.generateSpec(@tableMetaData)
      y: y.generateSpec(@tableMetaData)
      additionalInfo:
        joins: @joinsView.generateSpec()
    Events.ui.chart.add.trigger
      spec:
        layer: layer
    callback(true)

class QuickAddPieItemView extends QuickAddItemView
  constructor: (params) ->
    super(params)
    @metricView2.dropFilter = (dom) ->
      $(dom).data('dnd-data').meta.type in ['date', 'num']
  options1: () => CONST.layers.bar.color
  options2: () => CONST.layers.bar.y
  _addItem: (callback) =>
    col = @metricView1.metric()
    y   = @metricView2.metric()
    layer =
      type: 'bar'
      meta: @_makeMeta [col, y]
      color: col.generateSpec(@tableMetaData)
      y: y.generateSpec(@tableMetaData)
      additionalInfo:
        joins: @joinsView.generateSpec()
    Events.ui.chart.add.trigger
      spec:
        layer: layer
        coord:
          type: 'polar'
        guides:
          x:
            position: 'none'
            padding: 0
          y:
            position: 'none'
            padding: 0
    callback(true)

class QuickAddCommentView extends AbstractQuickAdd
  constructor: () ->
    @name = "Annotation"
    @imageClass = "large-icon img-icon-annotation"

  addItem: () =>
    Events.ui.quickadd.add.trigger {
      itemType: "CommentItem"
    }

class QuickAddNumeralView extends AbstractExpandableQuickAdd
  options: () => CONST.numeral.value
  constructor: (params) ->
    super(params)
    {tableMetaData} = params
    @name = "Number"
    @imageClass = "large-icon img-icon-numeral"
    @metricView = new QuickAddAesthetic(@, 'Value', @options, tableMetaData)
  onExpand: () =>
    @metricView.clear()
  onCollapse: () =>
    @metricView.disable()
  checkNewMetric: (event, item, callback) -> callback()
  checkRemoveMetric: ->
  addItem: () =>
    if @metricView.metric()
      # TODO: Get rid of terrrible, terrible hack that is proliferating
      x = @metricView.metric()
      if x.gaType not in ['none','ga-metric']
        TOAST.raise "Unable to create a Numeral without a number! Use a metric (orange) item!"
      else
        @_addItem()
        @successIndicatorVisible(true)
        Events.ui.dropdown.disable.trigger()
        @metricView.disable()
        setTimeout @collapse, 2000
  _addItem: () =>
    x = @metricView.metric()
    Events.ui.numeral.add.trigger
      spec:
        tableName: x.tableName
        data: x.jsdata
        value: x.generateSpec(@tableMetaData)
        meta: @_makeMeta [x]

class QuickAddTableView extends AbstractExpandableQuickAdd
  options: () => CONST.table.quickadd
  constructor: (params) ->
    super(params)
    {@tableMetaData} = params
    @name = "Table"
    @imageClass = "large-icon img-icon-table"
    @rows = ko.observableArray()
    @values = ko.observableArray()
    @canAdd = ko.computed () => @values().length and @rows().length
    @joinsView = new JoinsView(@tableMetaData, {}, @)
  onExpand: () =>
  onCollapse: () =>
    @rows.removeAll()
    @values.removeAll()
    if @joinsView?
      @joinsView.reset({})
  attachedMetrics: () => @rows().concat @values()
  addMetric: (event, item) =>
    @joinsView.checkAddJoins event, item, () =>
      @_addMetric(event, item)
  _addMetric: (event, item) =>
    columnInfo = @tableMetaData.getColumnInfo(item.data)
    aes = if columnInfo.meta.type is 'num' then 'values' else 'categories'
    metric = new QuickAddTableMetricView(columnInfo
                  , @options
                  , aes
                  , @attachedMetrics)
    Events.ui.metric.add.trigger() # mostly for NUX...
    Events.ui.metric.remove.onElem metric, @discardMetric
    if aes is 'categories'
      @rows.push(metric)
    else
      @values.push(metric)
    @_recalculateExpansion(event.target)
  discardMetric: (event, params) =>
    metric = params.dom.data('dndMetricObj') # TODO: HACK!
    if metric.aes is 'categories'
      @rows.remove(metric)
    else
      @values.remove(metric)
    @joinsView.checkRemoveJoins()
    @_recalculateExpansion(event.target)
  enabled: () -> @expanded()
  dropFilter: -> true
  addItem: (event) =>
    if @canAdd()
      @_addItem()
      @rows.removeAll()
      @values.removeAll()
      @successIndicatorVisible(true)
      @_recalculateExpansion(event.target)
      Events.ui.dropdown.disable.trigger()
      setTimeout @collapse, 2000
  _addItem: () =>
    rowspec = (metric.generateSpec(@tableMetaData) for metric in @rows())
    valuespec = (metric.generateSpec(@tableMetaData) for metric in @values())
    Events.ui.pivottable.add.trigger
      spec:
        tableName: metric.tableName
        data: metric.jsdata
        rows: rowspec
        values: valuespec
        meta: @_makeMeta @rows().concat(@values())
        additionalInfo:
          joins: @joinsView.generateSpec()


  initMetricItem: (metricDom, view) =>
    DND.makeDraggable(metricDom, view)
    view.attachDropdown(metricDom)

module.exports = QuickAddView
