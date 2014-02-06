AttachedMetricView = require('poly/main/data/metric/attached')
Events             = require('poly/main/events')
Parser             = require('poly/main/parser')

CONST              = require('poly/main/const')
DND                = require('poly/main/dnd')
TOAST              = require('poly/main/error/toast')

class AesGroupView
  constructor: (@aesName, @tableMetaData, @optionsValue, @parent) ->
    @enabled = ko.observable(true)
    @metrics = ko.observableArray()
    @metrics.subscribe ->
      Events.ui.chart.render.trigger()

  options: => @optionsValue

  reset: (specList, tableMeta) ->
    @metrics.removeAll()
    _.each specList, (spec) =>
      if spec.var
        name = Parser.getName(spec)
        tableName = spec.tableName ? tableMeta[polyjs.parser.unbracket(spec.var)].tableName
        params = data: {name, tableName}
        defaults =
          sort: spec.sort
          asc: spec.asc
          bin: Parser.getBinwidth(spec)
          stats: CONST.stats.statToName[Parser.getStats(spec)]
        @_actualMetricEnter(null, params, defaults)

  generateSpec: () =>
    m.generateSpec(@tableMetaData) for m in @metrics()

  onMetricEnter: (event, item, defaults={}) =>
    @parent.checkNewMetric event, item, () => # callback
      @_actualMetricEnter(event, item, defaults)

  _actualMetricEnter: (event, item, defaults={}) =>
    columnInfo = @tableMetaData.getColumnInfo(item.data)
    m = new AttachedMetricView(columnInfo
              , 'Table'
              , Events.ui.chart.render.trigger
              , @options
              , @parent.attachedMetrics
              , defaults)
    @metrics.push m
    Events.ui.metric.add.trigger() # mostly for NUX...
    Events.ui.metric.remove.onElem m, () =>
      @metrics.remove(m)
      @parent.checkRemoveMetric()

  disable: => @enabled(false)

  enable: => @enabled(true)

  initMetricItem:(dom, view) =>
    DND.makeDraggable(dom, view)
    view.attachDropdown(dom)

module.exports = AesGroupView
