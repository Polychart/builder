###
# Construciton of the Numeral Builder.
###
Aesthetic   = require('poly/main/chart/aes/base')
Animation   = require('poly/main/anim')
Builder     = require('poly/main/builder')
Events      = require('poly/main/events')
FiltersView = require('poly/main/chart/filters')
{JoinsView} = require('poly/main/chart/joins')
Parser      = require('poly/main/parser')
CONST       = require('poly/main/const')
TOAST       = require('poly/main/error/toast')

class NumeralBuilderView extends Builder
  item: 'numeral'
  constructor: (@tableMetaData) ->
    super(@tableMetaData)

    @value = new Aesthetic('value',( -> "Value"), @)
    @title = ko.observable "Untitled Numeral"
    @title.subscribe () => Events.ui.chart.render.trigger()
    @filtersView = new FiltersView(@tableMetaData, @)
    @joinsView = new JoinsView(@tableMetaData, {}, @)

  # for Aesthetic
  layerRestrictions: () => CONST.numeral
  attachedMetrics: () =>
    _.union _.compact([@value.metric()])
      , (f.metric() for f in @filtersView.filters())

  checkNewMetric: (event, item, callback) =>
    @joinsView.checkAddJoins(event, item, callback)

  checkRemoveMetric: (event, item) =>
    @joinsView.checkRemoveJoins()

  reset: (@params={}) ->
    #### Function to reset the Numeralbuilder state
    #
    # This is the main entry point for when we switch from the Dashboard view
    # to the Numeral builder view.
    @spec = @params.spec ? {}
    if @spec.value
      @value.init(@spec.value, @spec.tableName)
    @title @spec.title
    filter = @spec.filter ? {}
    @filtersView.reset(filter, @spec.meta)
    @joinsView.reset (@spec.additionalInfo?.joins)

  _render: (event, params) =>
    #### Internal function to transform builder state to Polychart2.js spec
    if (not @value?) or (not @value.metric()) then return  # Hacky fix to remove error.
    $dom = $(@dom)
    w = $dom.parent().width()
    h = $dom.parent().height()
    $dom.empty()

    valueMetric = @value.metric()
    if valueMetric.gaType? and valueMetric.gaType not in ['none','ga-metric']
      TOAST.raise "Unable to create a Numeral without a number! Use a metric (orange) item!"

    valueSpec = @value.generateSpec(@tableMetaData)

    meta = {}
    meta[valueMetric.fullFormula(@tableMetaData, true)] =
      _.extend valueMetric.fullMeta(),
        {dsKey: @tableMetaData.dsKey}
    meta = _.extend meta, @filtersView.generateMeta()

    filterSpec = @filtersView.generateSpec()

    @spec =
      filter:     filterSpec
      value:      valueSpec
      meta:       meta
      tableName:  valueMetric.tableName# hack
      data:       @tableMetaData.polyJsObjectFor {tableName: valueMetric.tableName}
      dom:        @dom
      width:      w
      height:     h
      title:      @title()
      additionalInfo:
        joins: @joinsView.generateSpec()
    spec = $.extend(true, {}, @spec)

    unless spec.title?
      name = Parser.getName(spec.value)
      spec.title = "#{name}"
      if not _.isEmpty(filterSpec) then spec.title += " - filtered"

    @loadingAnim.remove() if @loadingAnim
    @loadingAnim = new Animation('loading', $dom.parent())
    try
      c = polyjs.numeral spec, @loaded
      @_addTitleGlow c
    catch error
      TOAST.raise(error.message)

  _addListeners: (dom) =>
    #### Implementation for _addListeners from the general Builder
    #
    # Here, listeners that look for clicks on the Numeral title.
    @_addEventListener 'title-click', (e) =>
      if e.detail.type is 'guide-title' then @_editTitle e, @title, false

module.exports = NumeralBuilderView
