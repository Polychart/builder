# Top level view for viewing a particular chart
AbstractViewerEntryPoint = require('poly/main/main/viewer')

class ChartViewerMainView extends AbstractViewerEntryPoint
  constructor: (@params) ->
    super(@params)
    @spec = params.initial ? {}
    @tableMetaData = @dataView.getTableMetaData()

  init: (dom) =>
    initialCols = @spec.newcols ? []
    @dataView.initialize initialCols, () =>
      # instead of using spec.layer, use spec.layers
      if @spec.layer
        @spec.layers = [@spec.layer]
        delete @spec.layer
      # generate the polyJS object for each layer (given tableName)
      for layer in @spec.layers
        if not layer.data
          tableName = layer.tableName
          if not tableName? and layer.meta and m = _.toArray(layer.meta)[0]
            tableName = m.tableName
          layer.data = @tableMetaData.polyJsObjectFor {tableName}
      @spec.width ?= @params.width
      @spec.height ?= @params.height
      @spec.dom = dom[0]
      polyjs.chart(@spec)


module.exports = ChartViewerMainView
