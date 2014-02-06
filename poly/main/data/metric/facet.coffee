AttachedMetricView = require('poly/main/data/metric/attached')
Events             = require('poly/main/events')

CONST              = require('poly/main/const')

class FacetMetricView extends AttachedMetricView
  constructor: (columnInfo) ->
    updateFn = () => Events.ui.chart.render.trigger()
    options = () -> CONST.facets
    attachedMetrics = () -> []
    @removeText = "Remove \"" + columnInfo.name + "\" from facet"
    super columnInfo, @aes, updateFn, options, attachedMetrics

module.exports = FacetMetricView
