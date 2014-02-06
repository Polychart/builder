###
# Construciton of the Table Builder.
###
AesGroup    = require('poly/main/table/aesGroup')
Aesthetic   = require('poly/main/chart/aes/base')
Animation   = require('poly/main/anim')
Builder     = require('poly/main/builder')
Events      = require('poly/main/events')
FiltersView = require('poly/main/chart/filters')
{JoinsView} = require('poly/main/chart/joins')

CONST       = require('poly/main/const')
TOAST       = require('poly/main/error/toast')

PADDING = 10

class TableBuilderView extends Builder
  item: 'table'
  constructor: (@tableMetaData) ->
    super(@tableMetaData)

    @valuesView  = new AesGroup('Values', @tableMetaData, CONST.table.value, @)
    @columnsView = new AesGroup('Columns', @tableMetaData, CONST.table.column, @)
    @rowsView    = new AesGroup('Rows', @tableMetaData, CONST.table.row, @)
    @filtersView = new FiltersView(@tableMetaData, @)
    @joinsView = new JoinsView(@tableMetaData, {}, @)

  # for Aesthetic AND joins...
  attachedMetrics: () =>
    _.union @valuesView.metrics()
          , @columnsView.metrics()
          , @rowsView.metrics()
          , (f.metric() for f in @filtersView.filters())

  checkNewMetric: (event, item, callback) =>
    @joinsView.checkAddJoins(event, item, callback)

  checkRemoveMetric: (event, item) =>
    @joinsView.checkRemoveJoins()
  
  reset: (@params={}) ->
    #### Function to reset the Tablebuilder state
    #
    # This is the main entry point for when we switch from the Dashboard view
    # to the Table builder view.
    @spec = @params.spec ? {}
    {tableName, meta} = @spec

    @valuesView.reset (@spec.values ? []), meta
    @columnsView.reset (@spec.columns ? []), meta
    @rowsView.reset (@spec.rows ? []), meta
    @joinsView.reset (@spec.additionalInfo?.joins)

    # FILTER
    filter = @spec.filter ? {}
    @filtersView.reset(filter, @spec.meta)
    Events.ui.table.focus.trigger name: tableName

  _render: (event, params) =>
    #### Internal function to transform builder state to Polychart2.js spec
    $dom = $(@dom)
    w = $dom.parent().width() - PADDING*2
    h = $dom.parent().height() - PADDING*2
    $dom.empty()

    meta = {}
    metrics = _.union @valuesView.metrics()
                    , @columnsView.metrics()
                    , @rowsView.metrics()
    for metric in metrics
      meta[metric.fullFormula(@tableMetaData, true)] =
        _.extend metric.fullMeta(),
          {dsKey: @tableMetaData.dsKey}
    if not metric then return
    meta = _.extend meta, @filtersView.generateMeta()

    filterSpec = @filtersView.generateSpec()
    # putting them together
    @spec =
      meta:       meta
      tableName:  metric.tableName# hack
      data:       @tableMetaData.polyJsObjectFor {tableName: metric.tableName}
      filter:     filterSpec
      values:     @valuesView.generateSpec()
      columns:    @columnsView.generateSpec()
      rows:       @rowsView.generateSpec()
      dom:        @dom
      width:      w
      height:     h
      additionalInfo:
        joins: @joinsView.generateSpec()

    spec = $.extend(true, {}, @spec)
    @loadingAnim.remove() if @loadingAnim
    @loadingAnim = new Animation('loading', $dom.parent())
    try
      polyjs.pivot spec, @loaded
    catch error
      TOAST.raise(error.message)

module.exports = TableBuilderView
