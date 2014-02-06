Aesthetic      = require('poly/main/chart/aes/base')
ColorAesthetic = require('poly/main/chart/aes/color')
Events         = require('poly/main/events')
FiltersView    = require('poly/main/chart/filters')
SizeAesthetic  = require('poly/main/chart/aes/size')
{JoinsView}    = require('poly/main/chart/joins')

CONST          = require('poly/main/const')
TOAST          = require('poly/main/error/toast')

class LayerView
  #### View Model for Individual Layers
  #
  # This class defines the underlying model logic for layer.tmpl.
  #
  # :constructor params:
  #  :tableMetaData: Object
  #    Singleton used to reference the datasource. See poly.data.dataView for
  #    more information.
  #
  #  :layerspec: Object
  #    Object that contains properties defining the layer. Usually looks like
  #
  #      _added: <int>
  #      _depth: <ko.computed>
  #      type:   [bar|scatter|line|area|spline] (see CONST.layers)
  #      [x|y|color|size]:
  #        var:       <string>
  #        name:      <string>
  #        tableName: <string>
  #      data: <polyjs.data.api>
  #      meta:
  #        columnName1:
  #          type:      [cat|num|date]
  #          dsKey:     <string>
  #          tableName: <string>
  #
  #    The _added and _depth fields are used internally in this class to
  #    determine which place this Layer is in with respect to all other layers.
  #    All other properties are used for Polychart2.js rendering.
  #
  #  :polar: ko.observable(Boolean)
  #    An observable that indicates the coordinate type the chart is in. This is
  #    controlled exclusively by the layer with layerspec_depth == 0; all other
  #    layers will conform to the type at hand.
  constructor: (@tableMetaData, layerspec, @polar) ->
    _capitalize = (s) -> s.charAt(0).toUpperCase() + s.slice(1)
    _makeOption = (polar) -> (alist) ->
      # Helper function that produces ["Name", "value"] association list required
      # for DropdownSingle type menus.
      if not (alist[0]? and (alist[1]? or not polar)) then return  # Not allowed for polar
      value = alist[0]
      display = _capitalize(if polar then alist[1] else alist[0])
      [display, value].concat(if polar then [display.toLowerCase()] else [])

    _rectNames  = _.map CONST.layers.names, (item) -> item[0]

    # Initial value gleaned from the layerspec provided.
    t = if layerspec.type is 'point' then 'scatter' else layerspec.type
    initialType = _makeOption(@polar())(\
      CONST.layers.names[_rectNames.indexOf(t ? 'bar') ? 0])

    @layerspec = ko.observable(layerspec)
    @data      = ko.observable(layerspec.data)
    @meta      = ko.observable(layerspec.meta)

    @type = ko.observable(initialType)
    @type.subscribe (newValue) =>
      if @layerspec()._depth() is 0
        sel = newValue[0].toLowerCase()
        if sel in _rectNames
          @polar false
        else
          @polar true
      Events.ui.chart.render.trigger()

    @polar.subscribe (isPolar) =>
      if @layerspec()._depth() isnt 0
        polarType = CONST.layers.names[_rectNames.indexOf(@type()[1])]
        # Check that not forbidden polar type.
        if polarType[1] is null then polarType = CONST.layers.names[0]
        @plotOptionSelected(_makeOption(isPolar)(polarType))

    @plotOptionsItem = ko.computed () =>
      names = _.map CONST.layers.names, _makeOption(@polar())
      if @layerspec()._depth() is 0
        names = names.concat _.map(CONST.layers.names, _makeOption(!@polar()))
      _.filter names, (item) -> item?
    @plotOptionSelected = ko.computed
      read:  ()      -> @type()
      write: (value) -> @type value
      owner: @

    @layerRestrictions = ko.computed () =>
      CONST.layers[@type()[0].toLowerCase()]

    @filtersView = new FiltersView(@tableMetaData, @)
    @filtersView.reset((@layerspec().filter ? {}), @meta())

    xName     = ko.computed () => if @polar() then "Radius" else "X Axis"
    yName     = ko.computed () => if @polar() then "Angle" else "Y Axis"
    colorName = ko.computed () => if @polar() then "Color" else "Color"
    sizeName  = ko.computed () => "Size"
    @aesthetics =
      x:     new Aesthetic('x', xName, @)
      y:     new Aesthetic('y', yName, @)
      color: new ColorAesthetic('color', colorName, @)
      size:  new SizeAesthetic('size', sizeName, @)

    @visibleAesthetics = ko.computed () =>
      (@aesthetics[i] for i in @layerRestrictions().visibleAes)
    @attachedMetrics = ko.computed () =>
      aes = _.compact(aesView.metric() for aesView in @visibleAesthetics())
      filter = (f.metric() for f in @filtersView.filters())
      _.union(aes, filter)

    for aes, view of @aesthetics
      # Fix meta for compatibility reasons
      if layerspec[aes]? and not layerspec[aes].tableName and layerspec.tableName
        layerspec[aes].tableName = layerspec.tableName
      if layerspec[aes] and not layerspec[aes].dsKey
        layerspec[aes]?.dsKey = @tableMetaData.dsKey
      view.init(layerspec[aes], layerspec[aes]?.tableName)

    joinSpec   = layerspec.additionalInfo?.joins
    @joinsView = new JoinsView(@tableMetaData, joinSpec, @)

    @renderable = ko.computed () =>
      if 'ga' not of @meta and not @joinsView.renderable()
        false
      else if @attachedMetrics().length < 2
        false
      else
        Events.ui.chart.render.trigger()
        true
    return

  checkNewMetric: (event, item, callback) =>
    @joinsView.checkAddJoins(event, item, callback)

  checkRemoveMetric: (event, item) =>
    @joinsView.checkRemoveJoins()

  generateSpec: () =>
    layerspec =
      additionalInfo:  joins: @joinsView.generateSpec()
      type:            if @type()[1] is 'scatter' then 'point' else @type()[1]
      filter:          @filtersView.generateSpec()
      meta:            {}
    for aesView in @visibleAesthetics()
      spec = aesView.generateSpec()
      if spec
        layerspec[aesView.aes] = spec
        m = aesView.metric()
        if m?
          layerspec.meta[m.fullFormula(@tableMetaData, true)] =
            _.extend m.fullMeta()
                  , {dsKey: @tableMetaData.dsKey}
          layerspec.data = @tableMetaData.polyJsObjectFor {tableName: spec.tableName}
    layerspec.meta = _.extend layerspec.meta, @filtersView.generateMeta()
    if layerspec.data and layerspec.meta? and @renderable()
      if _.every(_.values(layerspec.meta), (item) -> 'ga' of item)
        if 'metric' not in _.map(layerspec.meta, (val) -> val.ga)
          TOAST.raise "Google Analytics charts require at least one metric—orange—item!"
          return {}
      layerspec
    else
      {}

  removeLayer: () =>
    Events.ui.layer.remove.triggerElem @, layer: @
    return

  disable: =>
    #### Helper to disable draggability of aesthetics.
    _.each @aesthetics, (aes) => aes.disable()
    @filtersView.disable()
    return

  enable: =>
    #### Helper to enable draggability of aesthetics.
    _.each @aesthetics, (aes) => aes.enable()
    @filtersView.enable()
    return

module.exports = LayerView
