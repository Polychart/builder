Events          = require('poly/main/events')
LayerMetricView = require('poly/main/data/metric/layer')
Parser          = require('poly/main/parser')

CONST           = require('poly/main/const')
DND             = require('poly/main/dnd')
TOAST           = require('poly/main/error/toast')

class Aesthetic
  #### Base View Model for Aesthetics
  #
  # This class defines the base model for all aesthetics on a layer. The class
  # will implement the logic with regards to dragging and dropping metrics onto
  # the aesthetics slots on each layer.
  #
  # :constructor params:
  #   :aes: String [x|y|color|size]
  #     Defines the aesthetic for which this model represents.
  #
  #   :name: ko.computed(String)
  #     Defines the name for the label of this model.
  #
  #   :layer: LayerView
  #     A reference to the LayerView model for which this aesthetic is part of.
  #     NOTE: This might also be a NumeralBuilderView object
  template:       'tmpl-aesthetic'
  metricTemplate: 'tmpl-metric-attached'
  constructor: (@aes, @name, @layer) ->
    @metric = ko.observable(null)
    @metric.subscribe (m) => Events.ui.metric.remove.onElem m, @onMetricDiscard

    @options = ko.computed () =>
      @layer.layerRestrictions()[@aes]
    @options.subscribe @layerTypeUpdated

    @enabled = ko.observable(true)

  init: (spec={}, tableName) =>
    if spec.var and tableName
      name     = Parser.getName(spec) # for backward compatibility!
      defaults =
        sort:  spec.sort
        asc:   spec.asc
        bin:   Parser.getBinwidth(spec)
        stats: CONST.stats.statToName[Parser.getStats(spec)]
      columnInfo = @layer.tableMetaData.getColumnInfo({name, tableName})
      metric = new LayerMetricView(columnInfo, @options, @layer, @name(), defaults)
      @metric(metric)
    else if spec.const
      @_setConstant(spec)
  generateSpec: () =>
    if @metric() then @metric().generateSpec(@layer.tableMetaData)
    else              @_getConstant()
  _setConstant: (spec) =>
  _getConstant: () => null

  onMetricEnter: (event, item) =>
    acceptableTypes = @options().type
    if not (item.data.meta.type in acceptableTypes)
      TOAST.raise("Data type is not one of the acceptable types!")
      return
    @layer.checkNewMetric event, item, () => # callback
      @_actualMetricEnter(event, item)

  _actualMetricEnter: (event, item) =>
    if @metric()
      @metric().close()
    m = new LayerMetricView(item.data, @options, @layer, @name())
    @metric(m)
    Events.ui.metric.add.trigger() # mostly for NUX...
    @render()

  onMetricDiscard: (event, metricItem) =>
    @metric().close()
    @metric(null)
    @layer.checkRemoveMetric(event, metricItem)
    @render()
  initMetricItem:(dom, view) =>
    DND.makeDraggable(dom, view)
    view.attachDropdown(dom)

  layerTypeUpdated: () =>
    if not @metric() then return
    # if layer type is updated and the current bound metric is no longer
    # of an acceptable type, then unbind it
    acceptableTypes = @options().type
    if not(@metric().type in acceptableTypes)
      @metric(null)

  render: () => Events.ui.chart.render.trigger()
  afterRender: (dom) ->

  disable: () => @enabled(false)
  enable:  () => @enabled(true)

  dropFilter: -> true

module.exports = Aesthetic
