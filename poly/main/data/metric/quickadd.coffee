AttachedMetricView = require('poly/main/data/metric/attached')

class QuickAddMetricView extends AttachedMetricView
  constructor: (columnInfo, @options, @aes) ->
    updateFn = () ->
    attachedMetrics = () -> []
    @removeText = "Remove \"" + columnInfo.name + "\" from " + @aes
    super columnInfo, @aes, updateFn, @options, attachedMetrics

module.exports = QuickAddMetricView
