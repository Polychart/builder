DND        = require('poly/main/dnd')
TOAST      = require('poly/main/error/toast')
Events     = require('poly/main/events')
MetricView = require('poly/main/data/metric/base')
ColumnInfo = require('poly/main/data/columnInfo')

class TableMetricListView
  constructor: (dataTable, @parent) ->
    {@name, meta, @jsdata} = dataTable

    @columnInfo = {}
    for name, params of meta
      @columnInfo[name] = new ColumnInfo({name, tableName: @name}, {meta: params})

    # metrics = things that already exists
    metrics = (new MetricView(@columnInfo[name]) for name of meta)
    metrics = _.sortBy metrics, (item) -> # sort GA metrics
      name = item.name
      if item.gaType != 'none'
        if item.gaType == 'ga-metric'
          name = '001_' + name
        else
          name = '002_' + name
      name
    @metrics = ko.observableArray(metrics)

    # derived metrics = new columns that users define
    @derivedMetrics = ko.observableArray()
    Events.data.column.new.onElem @, @newDerivedMetric
    Events.data.column.delete.onElem @, @deleteDerivedMetric

    # other metrics = fake columns that we define
    @otherMetrics = ko.observableArray()
    if _.isObject(meta) and _.every(_.values(meta), (val) -> 'ga' not of val)
      @columnInfo['count(*)'] =
        new ColumnInfo({name:'count(*)', tableName: @name}, {meta: {type: 'num'}})
      @otherMetrics.push new MetricView(@columnInfo['count(*)'])

    # combining all three
    @visibleMetrics = ko.computed () =>
      _.flatten [@metrics(), @derivedMetrics(), @otherMetrics()]
    @visibleMetrics.subscribe _.debounce(@_recalculateMaxHeight, 100, false)
    @metricNames = ko.computed () => _.pluck(@visibleMetrics(), 'name')

    @selected = ko.observable(no)
    @maxHeight = ko.observable(0)

    # Hide if not selected
    @renderHeight = ko.computed =>
      h = @maxHeight()
      if @selected()
        h
      else
        0

  newDerivedMetric: (event, params) =>
    {name, formula, type} = params
    if _.contains(@metricNames(), name)
      TOAST.raise "The column #{name} already exists in this table!"
      return
    @columnInfo[name] =
      new ColumnInfo({name, tableName: @name}, {
        meta: {type: type}
        formula: formula
      })
    m = new MetricView(@columnInfo[name])
    @derivedMetrics.push(m)
    #meta[formula] = type: type # do we need this?
    Events.data.column.update.trigger() if event?

  deleteDerivedMetric: (event, params) =>
    metric = params.metric
    unless metric and _.contains(@derivedMetrics(), metric)
      TOAST.raise "There are no such column to be deleted"
      return
    @derivedMetrics.remove(metric)
    delete @columnInfo[metric.name]
    Events.data.column.update.trigger() if event?

  serialize: () =>
    # serialize the derived columns
    for metric in @derivedMetrics()
      tableName: metric.tableName
      name: metric.name
      formula: metric.columnInfo.formula
      type: metric.columnInfo.meta.type

  afterRender: (@domElement) ->
    @_recalculateMaxHeight()

  _recalculateMaxHeight: () =>
    domElementInView = @domElement
    # Find appropriate element
    if $(domElementInView).hasClass('table-metric-list')
      metricsList = $(domElementInView).find('.metrics')
    else
      metricsList = $(domElementInView).parents('.table-metric-list').find('.metrics')

    # Match max-height to height of contents
    desiredHeight = metricsList.children().height()

    # Resize with animation
    @maxHeight(desiredHeight)

  select: (view, event) =>
    Events.ui.table.open.trigger info: name: @name
    @parent.clearSelection()
    @selected(yes)
    @_recalculateMaxHeight()

  getColumnInfo: (dsInfo) =>
    {tableName, name} = dsInfo
    if @columnInfo[name]? then return @columnInfo[name]
    tableNameReg      = new RegExp "#{tableName}\\.(.*)"
    match             = tableNameReg.exec(name)
    if match? then name = match[1]
    if @columnInfo[name]?
      return @columnInfo[name]
    TOAST.raise("Column #{name} does not exist within table #{tableName}")
    return

  initMetric: (domElements, metric) ->
    DND.makeDraggable(domElements, metric)
    # show tooltip if text has overflown or will almost overflow
    if metric.name.length > 15
      metricNameDom = $('.metric-name', domElements)
      $(domElements).tooltip
        position:
          my: "right+10 center"
          at: "left center"
          using: (position, feedback) ->
            $(@).css(position)
            $('<div>')
              .addClass('tooltip-arrow-left')
              .addClass(feedback.vertical)
              .addClass(feedback.horizontal)
              .appendTo(@)
        show: false
        hide: false

  openDataTableViewer: () =>
    Events.nav.datatableviewer.open.trigger {table: @}

module.exports = TableMetricListView
