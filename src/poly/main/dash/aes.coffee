Events             = require('poly/main/events')
QuickAddMetricView = require('poly/main/data/metric/quickadd')

CONST              = require('poly/main/const')
DND                = require('poly/main/dnd')
TOAST              = require('poly/main/error/toast')

class QuickAddAesthetic
  constructor: (@parent, @aes, @options, @tableMetaData) ->
    @metric = ko.observable()
    @metric.subscribe @parent.addItem
    @enabled = ko.observable false

  clear: () =>
    @metric null
    @enable()

  onMetricEnter: (event, item) =>
    if not @enabled() then return
    @parent.checkNewMetric event, item, () => # callback
      @_actualMetricEnter(event, item)

  _actualMetricEnter: (event, item) =>
    if @metric()
      @metric().close()
    # TODO: Make sure that removing table check
    columnInfo = @tableMetaData.getColumnInfo(item.data)
    @metric(new QuickAddMetricView(columnInfo, @options, @aes))
    Events.ui.metric.add.trigger() # mostly for NUX...
    Events.ui.metric.remove.onElem @metric(), @onMetricDiscard
    @parent._recalculateExpansion event.target

  onMetricDiscard: (event, metricItem) =>
    @metric().close()
    @clear()
    @parent.checkRemoveMetric()
    @parent._recalculateExpansion event.target

  initMetricItem: (dom, quickAddMetricView) =>
    DND.makeDraggable dom, quickAddMetricView
    quickAddMetricView.attachDropdown dom

  disable: =>
    @enabled false

  enable: =>
    @enabled true

  dropFilter: -> true


module.exports = QuickAddAesthetic
