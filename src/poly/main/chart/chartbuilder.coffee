###
# Construciton of the Chart Builder.
###
AdvancedPanelView = require('poly/main/chart/advancedPanel')
Animation         = require('poly/main/anim')
Builder           = require('poly/main/builder')
Events            = require('poly/main/events')
LayerView         = require('poly/main/chart/layer')
Parser            = require('poly/main/parser')

TOAST             = require('poly/main/error/toast')

class ChartbuilderView extends Builder
  item: 'chart'
  constructor: (@tableMetaData) ->
    super(@tableMetaData)
    @advancedPanel = new AdvancedPanelView(@tableMetaData)

    ## Set up local variables and UI observables
    @layers = ko.observableArray()
    @polar  = ko.observable(false)
    @title  = ko.observable "Untitled Chart"

    @vLabel = ko.observable()
    @hLabel = ko.observable()
    @guides = ko.observable({})

    ## Set up events
    _chartRender = () => Events.ui.chart.render.trigger()
    @title.subscribe  _chartRender
    @hLabel.subscribe _chartRender
    @vLabel.subscribe _chartRender

    @backButtonVisible = ko.observable(true)
    Events.ui.quickadd.expand.onElem @advancedPanel, @disableLayerDraggables
    Events.ui.quickadd.collapse.onElem @advancedPanel, @enableLayerDraggables

    @addLayer()

  reset: (@params={}) ->
    #### Function to reset the Chartbuilder state
    #
    # This function is called upon changing from the Dashboard Builder view to
    # the Chartbuilder View. The `params` object may contain the spec field,
    # which is a Polychart2.js specification object; if this is empty, then
    # the Chartbuilder will initialize in the empty state.
    @spec = @params.spec ? {}

    coord = @spec.coord ? {}
    @polar(coord.type is 'polar')
    @advancedPanel.coordView.reset(coord)

    layerspec =
      if @spec.layers? and _.isArray @spec.layers
        @spec.layers
      else if @spec.layer?
        [@spec.layer]
      else
        []
    @layers.removeAll()
    if _.isArray(layerspec) and layerspec.length > 0
      _.each layerspec, @addLayer
    else
      @addLayer()

    facet = @spec.facet ? {}
    @advancedPanel.facetView.reset(facet)

    @title @spec.title
    if @spec.guides?
      @guides(@spec.guides ? {})
      if coord.flip
        @vLabel @spec.guides.x?.title
        @hLabel @spec.guides.y?.title
      else
        @vLabel @spec.guides.y?.title
        @hLabel @spec.guides.x?.title
    else
      @vLabel null
      @hLabel null

  #### Layer functions

  addLayer: (spec={}) =>
    #### Helper to add a layer
    tmp = _.clone spec
    tmp._added = @layers().length
    tmp._depth = ko.computed do (tmp) => () =>
      for layer, i in @layers()
        if _.isEqual tmp._added, layer.layerspec()._added
          return i
      return -1
    newLayer = new LayerView(@tableMetaData, tmp, @polar)
    @layers.push(newLayer)
    Events.ui.layer.remove.onElem newLayer, (event, params) =>
      {layer} = params
      @removeLayer(layer)

  removeLayer: (layer) =>
    #### Helper to remove a layer
    @layers.remove(layer)
    @render()

  enableLayerDraggables: =>
    #### Helper to enable draggability of aesthetics.
    _.each @layers(), (layer) => layer.enable()
    return

  disableLayerDraggables: =>
    #### Helper to disable draggability of aesthetics.
    _.each @layers(), (layer) => layer.disable()
    return

  serialize: () ->
    #### Serialize the state of Chartbuilder
    # TODO: refactor shared code /dash/chart.coffee
    spec = $.extend(true, {}, @spec)
    delete spec.dom
    delete spec.data
    if spec.layer
      delete spec.layer.data
    if spec.layers
      for layers in spec.layers
        delete layers.data
        delete layers._added
        delete layers._depth
    spec


  #### Helpers for initializing and rendering the Chartbuilder.


  _render: (event, params) =>
    #### Internal helper to render the Chartbuilder state in Polychart2.js
    #
    # This function transforms the specifications of each
    # component---the advancedPanelView, coordView, joinsView and
    # layersView---into into a single object that Polychart2.js understands.
    # See the middle of this function for the required form.
    $dom = $(@dom)
    w = $dom.parent().width()
    h = $dom.parent().height()
    $dom.empty()

    layers     = []
    for layer in @layers()
      tmp = layer.generateSpec()
      unless _.isEmpty(tmp)
        tmp.meta = _.extend tmp.meta, @advancedPanel.facetView.generateMeta()
        layers.push tmp

    coord = _.extend( @advancedPanel.coordView.generateSpec()
                    , type: (if @polar() then 'polar' else 'cartesian'))
    facet = @advancedPanel.facetView.generateSpec()

    if params is 'flip'
      tmp = @hLabel()
      @hLabel @vLabel()
      @vLabel tmp

    guides = @guides()
    if params?.guides and params.guides != {}
      @guides _.extend(guides, params.guides)
    else if coord.type is 'polar' # Remove labels by default, but preserve
      x = position: 'none', padding: 0
      y = position: 'none', padding: 0
      if coord.flip
        [x.title, y.title] = [@vLabel(), @hLabel()]
      else
        [x.title, y.title] = [@hLabel(), @vLabel()]
      guides = _.extend guides, {x, y}
      @guides guides
    else if coord.flip
      guides = _.extend guides, {x: {title: @vLabel()}, y: {title: @hLabel()}}
      @guides guides
    else
      guides = _.extend guides, {x: {title: @hLabel()}, y: {title: @vLabel()}}
      @guides guides

    # Remove null titles
    guides = @guides()
    for key, val of guides
      unless val.title?
        delete guides[key].title
    @guides(guides)

    if layers.length > 0
      @spec =
        layers: layers
        coord:  coord
        guides: @guides()
        facet:  facet
        dom:    @dom
        width:  w
        height: h
        title:  @title()
        zoom: false
      spec = $.extend(true, {}, @spec)
      unless spec.title?
        getName = (v) ->
          if v?
            "#{Parser.getName(v)}"
          else
            ""
        l = layers[0]
        if coord?.type == 'polar' && l.color?
          spec.title = "#{getName(l.y)} by #{getName(l.color)}"
        else
          spec.title = "#{getName(l.y)} by #{getName(l.x)}"
      @loadingAnim.remove() if @loadingAnim
      @loadingAnim = new Animation('loading', $dom.parent())
      try
        c = polyjs.chart spec, @loaded
        @_addTitleGlow c
      catch error
        TOAST.raise(error.message)

  _addListeners: (dom) =>
    #### Implementation for _addListeners from the general Builder
    #
    # Here, listeners that look for clicks on the Chart titles, Legend titles,
    # and Axes titles are attached to the chart DOM.
    @_addEventListener 'title-click', (e) =>
      [titleHolder, rotated] = switch e.detail.type
        when 'guide-title'  then [@title, false]
        when 'guide-titleH' then [@hLabel, false]
        when 'guide-titleV' then [@vLabel, true]
      @_editTitle e, titleHolder, rotated
    @_addEventListener 'legend-click', (e) =>
      legendHolder = ko.observable()
      legendHolder.subscribe (newName) =>
        guides = @guides()
        obj = e.detail.data
        if e.detail.type is 'legend-label'
          for key, data of obj.evtData
            guides[data.aes] ?= labels: {}
            guides[data.aes].labels[data.value] = newName
        else if e.detail.type is 'legend-title'
          guides[obj.evtData.aes] ?= labels: {}
          guides[obj.evtData.aes].title = newName
        @guides guides
        @render()
      @_editTitle e, legendHolder, false

module.exports = ChartbuilderView
