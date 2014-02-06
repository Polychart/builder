AttachedMetricView = require('poly/main/data/metric/attached')

class QuickAddTableMetricView extends AttachedMetricView
  constructor: (columnInfo, @options, @aes, attachedMetrics) ->
    updateFn = () ->
    @removeText = "Remove \"" + columnInfo.name + "\" from " + @aes
    super columnInfo, @aes, updateFn, @options, attachedMetrics

module.exports = QuickAddTableMetricView
