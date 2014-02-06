# Top level view for Polychart Dashboard Builder
AbstractBuilderEntryPoint = require('poly/main/main/builder')
ChartbuilderView          = require('poly/main/chart/chartbuilder')
DashboardView             = require('poly/main/dash/dashboard')
DataTableView             = require('poly/main/data/datatableView')
Events                    = require('poly/main/events')
NumeralbuilderView        = require('poly/main/numeral/numeralbuilder')
TablebuilderView          = require('poly/main/table/tablebuilder')
{RemoteDataSource}        = require('poly/main/data/dataSource')

CONST                     = require('poly/main/const')
TOAST                     = require('poly/main/error/toast')
TUTORIAL                  = require('poly/main/main/tutorial')

NuxView                   = require('poly/nux')

serverApi                 = require('poly/common/serverApi')

class DashMainView extends AbstractBuilderEntryPoint
  constructor: (@params) ->
    @params.header ?= true
    {@isDemo, @local, @customSaving, @dataCollection} = @params
    @local ?= false

    super(@params)

    @name = ko.observable @params.name
    @name.subscribe (val) => _.debounce(@_save, 300)

    @dashKey = @params.key

    tableMetaData = @dataView.getTableMetaData()

    @dashViewHref = "/dashboard/#{@dashKey}/view"
    @dashboardView = new DashboardView(@name, tableMetaData)
    @dashVisible = ko.observable(true)

    @chartbuilderView = new ChartbuilderView(tableMetaData)
    @chartbuilderVisible = ko.observable(false)

    @numeralbuilderView = new NumeralbuilderView(tableMetaData)
    @numeralbuilderVisible = ko.observable(false)

    @tablebuilderView = new TablebuilderView(tableMetaData)
    @tablebuilderVisible = ko.observable(false)

    @dataTableView = new DataTableView(tableMetaData)
    @dataTableViewVisible = ko.observable(false)

    Events.ui.ga.notify.on (event, params) =>
      # If more than just TitleItem in dashboard
      # TODO Proper check if tutorial needed
      if _.size(@params.initial) > 0
        return

      gaNuxSteps = [{
        cover: 'HEADER, .content-panel'
        template: 'tmpl-nux-ga'
        buttonText: 'I understand'
        onFinish: ->
          Events.ui.ga.done.trigger()
        ref: '.content-panel'
        top: 20
        left: 25
        arrowDir: 'left'
      }]
      @nuxView(new NuxView({
        steps: gaNuxSteps
        onSkip: =>
          Events.ui.nux.skip.trigger()
      }))

    Events.nav.chartbuilder.open.on (event, params)   => @loadChartbuilder(params)
    Events.nav.numeralbuilder.open.on (event, params) => @loadNumeralbuilder(params)
    Events.nav.tablebuilder.open.on (event, params) => @loadTablebuilder(params)

    Events.nav.datatableviewer.open.on (event, params) => @loadDataviewer(params)
    Events.nav.datatableviewer.close.on (event, params) => @closeDataviewer(params)

    Events.nav.dashbuilder.open.on @closeBuilder
    Events.nav.home.open.on =>
      @_save (err, result) =>
        unless err
          window.location.href = '/home'

    Events.nav.dashviewer.open.on (event, params) =>
      window.location = "/dashboard/#{encodeURIComponent(@dashKey)}/view"

    # Serialize and post to server when user edits dashboard
    saveWorthyEvents = [
      # Is YOUR event worthy of a save?  Add it here.
      Events.model.dashboarditem.create
      Events.model.dashboarditem.update
      Events.model.dashboarditem.delete
      Events.data.column.update
    ]
    for swe in saveWorthyEvents
      swe.on => @_save()
    @initialize()

  initialize: () =>
    initial = @params.initial ? []
    if _.isArray(@params.initial)
      initialItems = @params.initial
      initialCols = []
    else if _.isObject(@params.initial)
      initialItems = @params.initial.items ? []
      initialCols = @params.initial.newcols ? []

    @dataView.initialize initialCols, () => @dashboardView.initialize(initialItems)
    if @params.showTutorial
      @nuxView = ko.observable(new NuxView({
        steps: TUTORIAL(@local)
        onSkip: =>
          Events.ui.nux.skip.trigger()
          if not @local
            serverApi.sendPost '/tutorial/mark-complete', {type: 'nux'}, (err) ->
              console.error err if err
      }))
    else
      @nuxView = ko.observable(null)

  # Don't call this from other classes.
  # Instead, trigger an event, and add it as a saveWorthyEvent
  _save: (callback) =>
    if @isDemo or (@local and not @customSaving)
      callback() if callback
      return

    serialized = {
      name: @name()
      spec: @serialize()
      dataCollection: {
        dataSourceKey
        tableNames
      } for {dataSourceKey, tableNames} in @dataCollection
    }

    if @customSaving
      @customSaving serialized
      callback() if callback
      return

    serverApi.sendPost(
      "/dashboard/#{encodeURIComponent(@dashKey)}/update",
      serialized,
      (err, res) ->
        if err
          TOAST.raise 'Error while saving dashboard'
        if callback
          callback err, res
    )

  closeBuilder: (event, params) =>
    if params.from is 'chart'
      @closeChartbuilder()
    else if params.from is 'numeral'
      @closeNumeralbuilder()
    else
      @closeTablebuilder()

  loadChartbuilder: (params) =>
    @chartbuilderView.reset(params)
    @chartbuilderVisible(true)
    @dashVisible(false)

  closeChartbuilder: () =>
    spec = @chartbuilderView.spec
    if spec and spec.layers and spec.layers.length > 0
      chartView = @chartbuilderView.params.chartView
      if chartView?
        chartView.setSpec spec
      else
        Events.ui.chart.add.trigger {spec: spec}
    @chartbuilderVisible(false)
    @dashVisible(true)

  loadTablebuilder: (params) =>
    @tablebuilderView.reset(params)
    @tablebuilderVisible(true)
    @dashVisible(false)

  closeTablebuilder: () =>
    spec = @tablebuilderView.spec
    tableView = @tablebuilderView.params.tableView
    if spec and (_.size(spec.values ? []) + _.size(spec.rows ? []) + _.size(spec.columns ? [])) > 0
      if tableView?
        tableView.setSpec spec
      else
        params =
          spec: spec
        Events.ui.pivottable.add.trigger params
    @tablebuilderVisible(false)
    @dashVisible(true)

  loadNumeralbuilder: (params) =>
    @numeralbuilderView.reset(params)
    @numeralbuilderVisible(true)
    @dashVisible(false)

  closeNumeralbuilder: () =>
    spec = @numeralbuilderView.spec
    numeralView = @numeralbuilderView.params.numeralView
    if numeralView?
      numeralView.setSpec spec
    else
      Events.ui.numeral.add.trigger {spec: spec}
    @numeralbuilderVisible(false)
    @dashVisible(true)

  loadDataviewer: (params={}) =>
    if not @dataTableViewVisible()
      params.previous =
        if @dashVisible()
          @dashVisible(false)
          'dash'
        else if @numeralbuilderVisible()
          @numeralbuilderVisible(false)
          'numeral'
        else if @chartbuilderVisible()
          @chartbuilderVisible(false)
          'chart'
        else if @tablebuilderVisible()
          @tablebuilderVisible(false)
          'table'
    @dataTableViewVisible(true)
    @dataTableView.reset(params)

  closeDataviewer: (params) =>
    @dataTableViewVisible(false)
    switch params.previous
      when 'dash' then @dashVisible(true)
      when 'numeral' then @numeralbuilderVisible(true)
      when 'table' then @tablebuilderVisible(true)
      when 'chart' then @chartbuilderVisible(true)

  serialize: () =>
    items: @dashboardView.serialize()
    newcols: @dataView.serialize()


module.exports = DashMainView
