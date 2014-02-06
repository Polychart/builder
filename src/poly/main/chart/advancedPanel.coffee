Events          = require('poly/main/events')
FacetMetricView = require('poly/main/data/metric/facet')
Parser          = require('poly/main/parser')

DND             = require('poly/main/dnd')
CONST           = require('poly/main/const')

class AdvancedPanelView
  constructor: (@tableMetaData) ->
    @expanded = ko.observable(false)
    @facetView = new FacetView(@tableMetaData)
    @coordView = new CoordView()

class FacetView
  constructor: (@tableMetaData) ->
    @metric = ko.observable()
  metricTemplate: 'tmpl-metric-attached'
  onMetricEnter: (event, item) =>
    if @metric()
      @metric().close()
    m = new FacetMetricView(item.data)
    @metric(m)
    Events.ui.chart.render.trigger()
  onMetricDiscard: () =>
    @metric().close()
    @metric(null)
    Events.ui.chart.render.trigger()
  generateSpec: () =>
    if @metric()
      type: 'wrap'
      var: @metric().generateSpec()
      tableName: @metric().tableName
    else
      {}
  generateMeta: () =>
    meta = {}
    if m = @metric()
      meta[m.fullFormula(@tableMetaData, true)] =
        _.extend m.fullMeta()
              , {dsKey: @tableMetaData.dsKey}
    meta
  initMetricItem: (dom, view) =>
    DND.makeDraggable(dom, view)
    view.attachDropdown(dom)
  reset: (spec) =>
    if spec.var and spec.tableName
      name = Parser.getName(spec.var) # fml
      params = {name, tableName: spec.tableName}
      columnInfo = @tableMetaData.getColumnInfo(params)
      m = new FacetMetricView(columnInfo)
      @metric(m)
    else
      if @metric()
        @metric().close()
      @metric(null)

class CoordView
  constructor: () ->
    @flip = ko.observable(false)
    @flip.subscribe () => Events.ui.chart.render.trigger('flip')
  reset: (spec) =>
    @flip(!!spec.flip)
  generateSpec: () =>
    flip: @flip()
  flipClick: () =>
    @flip(!@flip())

module.exports = AdvancedPanelView


