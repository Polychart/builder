Events     = require('poly/main/events')
PolyJSItem = require('poly/main/dash/item/polyjs')
Parser     = require('poly/main/parser')
LayerView  = require('poly/main/chart/layer')

CONST      = require('poly/main/const')
TOAST      = require('poly/main/error/toast')

class ChartItem extends PolyJSItem
  minWidth: 8
  minHeight: 6
  templateName: 'tmpl-chart-item'
  constructor: (@spec=null, position={}) ->
    position.width or= 12
    position.height or= 8
    super(@spec, position)

  _initSpec: () =>
    @spec.paddingLeft ?= 0
    @spec.paddingRight ?= 0
    @spec.paddingTop ?= 0
    @spec.paddingBottom ?= 0
    # instead of using spec.layer, use spec.layers
    if @spec.layer
      @spec.layers = [@spec.layer]
      delete @spec.layer
    # generate the polyJS object for each layer (given tableName)
    for layer in @spec.layers
      if not layer.data
        tableName = layer.tableName
        for prop, val of layer
          if tableName? then break
          if _.isObject(val) and 'var' of val and 'tableName' of val
            tableName = val.tableName
        layer.data = @tableMetaData.polyJsObjectFor {tableName}
        for key, val of layer.meta
          layer.meta[key].dsKey = @tableMetaData.getDsKey

    # generate full meta for backwards compatibility
    for layer in @spec.layers
      for name, value of layer.meta
        try
          newname =
            if name is 'count(*)'
              'count(1)'
            else
              polyjs.parser.unbracket(polyjs.parser.parse(name).pretty())
          if not layer.meta[newname] and layer.meta[name]
            layer.meta[newname] = layer.meta[name]
        catch
          #do nothing

  _renderPolyJSItem: (spec, loaded, callback) =>
    spec = $.extend(true, {}, spec)
    # duplicated code from src/core/chart/chartbuilder.coffee
    unless spec.title?
      getName = (v) ->
        if v? then "#{Parser.getName(v)}"
        else       ""
      l = spec.layers[0]
      if spec.coord?.type is 'polar' && l.color?
        spec.title = "#{getName(l.y)} by #{getName(l.color)}"
      else
        spec.title = "#{getName(l.y)} by #{getName(l.x)}"
    spec.zoom = @isViewer()
    polyjs.chart spec, loaded, callback

  serialize: (s={}) =>
    spec = $.extend(true, s, @spec)
    delete spec.dom
    delete spec.data
    if spec.layer
      delete spec.layer.data
    if spec.layers
      for layers in spec.layers
        delete layers.data
    super
      itemType: 'ChartItem'
      spec: spec

  editChart: () =>
    Events.ui.chart.edit.trigger()
    Events.nav.chartbuilder.open.trigger {
      spec: @spec
      chartView: @
    }


module.exports = ChartItem
