AttachedMetricView = require('poly/main/data/metric/attached')
Events             = require('poly/main/events')

CONST              = require('poly/main/const')

class LayerMetricView extends AttachedMetricView
  constructor: (columnInfo, @options, @layer, @aesName, defaults) ->
    updateFn = () => Events.ui.chart.render.trigger()
    attachedMetrics = @layer.attachedMetrics
    super columnInfo, @aesName, updateFn, @options, attachedMetrics, defaults

module.exports = LayerMetricView
