Events = require('poly/main/events')

CONST  = require('poly/main/const')
TOAST  = require('poly/main/error/toast')
AUTOCOMPLETE = require('poly/main/data/autocomplete')
{ extractLast, autocompleteSelect} = AUTOCOMPLETE

normalize = (str) -> polyjs.parser.parse(str).pretty()
getType = (str, typeEnv) ->
  polyjs.debug.parser.getType(str, typeEnv, false)

class DataTableView
  constructor: (@tableMetaData) ->
    @visible = ko.observable(false)
    @errorMessage = ko.observable(false)
    @autocompleteView = new AutocompleteView()
    @editView = new EditView()
    @canAddVar = @tableMetaData.dsType in ['local', 'mysql', 'postgresql', 'infobright']
    Events.data.column.update.on () => @render() if @visible()
  navigateBack: (event) =>
    Events.nav.datatableviewer.close.trigger {@previous}
    @visible(false)
  reset: (params) =>
    @visible(true)
    if params.previous? then @previous = params.previous
    @tableView = params.table
    @editView.reset(@tableView)
    @render()
  render: () =>
    {@name, jsdata, @columnInfo} = @tableView
    trans = []
    select = []
    meta = {}
    for colName, col of @columnInfo
      if colName isnt 'count(*)'
        key = col.getFormula(@tableMetaData)
        meta[polyjs.parser.unbracket key] = col.meta
        expr = polyjs.parser.getExpression(key).expr
        select.push(expr)
        if col.formula
          trans.push(expr)
    @autocompleteView.reset(@tableView)
    dataSpec =
      select: select
      stats:
        stats: []
        groups: []
      trans: trans
      filter: []
      limit: 200
      meta: meta
    jsdata.getData @processData, dataSpec

  _getFormatter: (type) ->
    if type is 'date'
      (row, cell, value, columnDef, dataContext) ->
        moment.unix(value).format()
    else
      (row, cell, value, columnDef, dataContext) -> value

  processData: (err, jsdata) =>
    if @visible()
      if err
        @errorMessage(err.message)
      else
        @errorMessage(false)
        slickcolumns = []
        for colName, col of @columnInfo
          if colName isnt 'count(*)'
            slickcolumns.push
              id: col.name
              name: col.name
              field: polyjs.parser.unbracket col.getFormula(@tableMetaData)
              formatter: @_getFormatter(col.meta.type)
              sortable: true
        @slickgrid.setColumns slickcolumns
        @slickgrid.setData jsdata.raw, true
        @slickgrid.render()
        @slickgrid.onSort.subscribe (e, args) =>
          cols = args.sortCols
          jsdata.raw.sort (r1, r2) =>
            for col in cols
              type = @columnInfo[col.sortCol.name].type
              sign = if col.sortAsc then 1 else -1
              v1 = r1[col.sortCol.field]
              v2 = r2[col.sortCol.field]
              result = polyjs.debug.type.compare(type)(v1,v2)*sign
              if result isnt 0
                return result
            return 0
          @slickgrid.setData jsdata.raw, true
          @slickgrid.invalidate()
          @slickgrid.render()

  initSlickgridDom: (@dom) =>
    @slickgrid = new Slick.Grid $(@dom), [], [], {
      multiColumnSort: true
    }

  initAutocomplete: (dom) => @autocompleteView.init(dom)

class EditView
  constructor: ->
    @tableView = ko.observable()
    @metricViews = ko.computed () =>
      tableView = @tableView()
      if tableView
        new EditMetric(tableView, m) for m in tableView.derivedMetrics()
      else
        []
  reset: (tableView) =>
    @tableView(tableView)

class EditMetric
  constructor: (@tableView, @metric) ->
  deleteMetric: () =>
    Events.data.column.delete.triggerElem @tableView, { @metric }

class AutocompleteView
  constructor: ->
    @alias = ko.observable('')
    @formula = ko.observable('')
    @errorMessage = ko.observable('')
    @colNames = []
    @typeEnv = null
  reset: (@tableView) =>
    @colNames = []
    colTypes = {}
    for metric in @tableView.metrics()
      n = polyjs.parser.escape(metric.name)
      @colNames.push(n)
      colTypes[metric.name] = type: metric.type
    @typeEnv = polyjs.debug.parser.createColTypeEnv colTypes
    @clear()
  clear: =>
    @alias('')
    @formula('')
    @formulaDom.val('') if @formulaDom
    @errorMessage('')
  openHelp: =>
    #### UI function to open the help doc overlay
    Events.ui.dialog.show.trigger
      template: 'tmpl-formula-docs'
      type:     'formula-docs'
      view:     @
  closeHelp: () =>
    #### UI function to close the help doc overlay
    Events.ui.dialog.hide.trigger()
  checkFormula: (value) =>
    try
      getType(value)
      @errorMessage ""
    catch error
      # there is an error
      @errorMessage error.message
  addItem: =>
    @errorMessage('') # make sure error message is clean
    name = @alias()
    f = @formula()
    if name == ''
      @errorMessage('You need a name for the new column!')
      return
    if _.contains(@tableView.metricNames(), name)
      @errorMessage("The column #{name} already exists in this table!")
      return
    try
      type = getType(f, @typeEnv)
    catch e
      @errorMessage("Error in your formula: #{e.message}")
      return
    if type is 'stat'
      @errorMessage("Your formula cannot contain aggregate statistics!")
      return
    Events.data.column.new.triggerElem @tableView, {
      name: @alias()
      formula: normalize(f)
      type: type
    }
    Events.data.column.add.trigger() # NUX
    @clear()
  init: (dom) =>
    # modified from chartbuilder/src/coffee/widget/tooltip.coffee
    self = @
    @formulaDom = $('.formula-input', dom)
    @formulaDom.autocomplete
      focus: ( -> false)
      source: (request, response) =>
        {selectionStart, selectionEnd} = @formulaDom[0]
        range = extractLast(request.term, selectionStart, selectionEnd)
        if not range
          response([])
        else
          tail = request.term.substring(range[0], range[1])
          #tail = polyjs.parser.unescape(tail)
          filtered = $.ui.autocomplete.filter(self.colNames, tail)
          response(filtered)
      select: (event, ui) ->
        # this = dom for jquery autocomplete?
        cursorLocation = autocompleteSelect.call(@, event, ui)
        self.formula(@value)
        @selectionStart = cursorLocation
        @selectionEnd = cursorLocation
        return false

module.exports = DataTableView
