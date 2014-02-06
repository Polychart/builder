DropdownMetricView = require('poly/main/data/metric/dropdown')
Events             = require('poly/main/events')
Parser             = require('poly/main/parser')

CONST              = require('poly/main/const')
DND                = require('poly/main/dnd')
TOAST              = require('poly/main/error/toast')

MIL_PER_SEC = 1000
SEC_PER_DAY = 60 * 60 * 24

DATE_FUNCTIONS = {}
for [range, timeDelta] in [
  ['Past Day'  , SEC_PER_DAY],
  ['Past Week' , SEC_PER_DAY * 7],
  ['Past Month', SEC_PER_DAY * 30],
  ['Past Year' , SEC_PER_DAY * 365]
]
  DATE_FUNCTIONS[range] = do (timeDelta) -> () ->
    moment().unix() - timeDelta

# Smallest date value which we assume to be in ms rather than seconds
# If this were treated as seconds (unix timestamp), it would be 2286-11-20T17:46:40Z
# In milliseconds (unix offset), it would be 1970-04-26T17:46:40Z
MINIMUM_MIL = Math.pow 10,10

SLIDER_DOM_SELECTOR = '.slider'
# TODO: Change the naming here
class FiltersView
  constructor: (@tableMetaData, @parent) ->
    @filters = ko.observableArray()
    @enabled = ko.observable(true)

  reset: (spec, tableMeta) =>
    @filters = ko.observableArray()
    for column, defaults of spec
      if defaults.tableName and column.indexOf(defaults.tableName) != -1
        tableName = defaults.tableName
      else
        tableName = Parser.getTableName(column)
      name = defaults.name ? Parser.getName(var: column)

      if not tableName # backwards compatibility
        # this is a drastic measure; and it doesn't work with joins
        value = _.find(tableMeta, (val, key) -> Parser.getName(key) is column)
        if value? and value.tableName?
          tableName = value.tableName
        else
          for key, val of tableMeta
            if val.tableName? then tableName = val.tableName; break

      columnInfo = @tableMetaData.getColumnInfo {tableName, name}
      @_actualMetricEnter(null, {data: columnInfo}, defaults)

  generateSpec: () =>
    spec    = {}
    filters = @filters()
    for filter in filters
      filterSpec = filter.generateSpec()
      unless _.isEmpty filterSpec
        m = filter.metric()
        spec[m.fullFormula(@tableMetaData)] = filterSpec
    return spec

  generateMeta: () =>
    meta = {}
    filters = @filters()
    for filter in filters
      m = filter.metric()
      if m
        meta[m.fullFormula(@tableMetaData, true)] =
          _.extend m.fullMeta()
                , {dsKey: @tableMetaData.dsKey}
    meta


  onMetricEnter: (event, item, defaults) =>
    # Check to see if item has been filtered already.
    if _.reduce(@filters(),
                  ((acc, f) ->
                    acc or  item.data.tableName is f.metric().tableName\
                        and item.data.name      is f.metric().name
                   ), false)
      TOAST.raise "You may not filter twice on the same metric!"
      return
    if item.data.name is 'count(*)'
      TOAST.raise "You can't filter on that item."
      return
    @parent.checkNewMetric event, item, () => # callback
      @_actualMetricEnter(event, item, defaults)

  _actualMetricEnter: (event, item, defaults={}) =>
    if _.isNumber defaults
      index = defaults
      f = new Filter(@tableMetaData, index + 1, {})
      f.onMetricEnter(event, item)
      filters = @filters.slice(0, index)
      filters.push(f)
      @filters(filters.concat @filters.slice(index + 1))
    else
      f = new Filter(@tableMetaData, @filters().length + 1, defaults)
      f.onMetricEnter(event, item)
      @filters.push f

    Events.ui.filter.remove.onElem f, (evt, params) =>
      if params? # Then exchanging filters
        index = @filters.indexOf(f)
        @onMetricEnter null, params, index
      else
        @filters.remove(f)

  dropFilter: (dom) =>
    $(dom).data('dnd-data').meta.type in ['date', 'num', 'cat']

  disable: => @enabled(false)
  enable:  => @enabled(true)

class Filter
  constructor: (@tableMetaData, id, @_defaults = {}) ->
    @render        = _.debounce @_render, 600
    @label         = "Filter " + id
    @metric        = ko.observable(false)
    @metaDone      = ko.observable(false)

    @showNotNull  = @tableMetaData.dsType in ['mysql', 'postgresql', 'infobright']
    @notNull      = ko.observable(@_defaults.notnull ? true)

    @sliderMin   = ko.observable(+@_defaults.min)
    @sliderMax   = ko.observable(+@_defaults.max)

    @filterMin   = ko.observable @sliderMin()
    @filterMax   = ko.observable @sliderMax()
    @filterRange = ko.computed
      read: () ->
        [@filterMin(), @filterMax()]
      write: (newVal) ->
        @filterMin newVal[0]
        @filterMax newVal[1]
      owner: @

    @filterDisplay = ko.computed () =>
      min = @filterMin()
      max = @filterMax()
      if @metric().type is "date"
        moment.unix(min).format("D MMM YYYY") + ' - '  + moment.unix(max).format("D MMM YYYY")
      else
        min + ' - ' + max

    @filterCatOptions = ko.observableArray()
    @filterCatValue   = ko.observableArray()

    @filterCatOptionsText = (v) ->
      if v
        v
      else
       "(NULL)"

    # The [["Display", "value"], ...] pairs needed for DropdownSingle.
    # The values will correspond to the lower bound for dates.
    # Options that are greater than @sliderMax are rejected.
    @dateOptions = ko.computed =>
      if @metric().type isnt 'date'
        return null
      opts = _.reject _.pairs(DATE_FUNCTIONS), (v) => v[1]() >= @sliderMax()
      opts.push ['Custom', null]
      opts

    @dateOptionSelected = ko.observable(['Custom', null])
    @dateOptionSelected.subscribe (newVal) =>
      if newVal[1]?
        @filterMin newVal[1]()

    @sliderVisible = ko.computed =>
      if not @sliderMin()? or not @sliderMax()?
        false
      else if @metric().type is 'date'
        @dateOptionSelected()[0] is 'Custom'
      else
        true
    @sliderVisible.subscribe @render

    # constrain value to range
    @sliderMin.subscribe (val) =>
      try
        $(SLIDER_DOM_SELECTOR, @dom).slider "min", @sliderMax()
        if @filterMin() < val
          @filterMin val
    @sliderMax.subscribe (val) =>
      try
        $(SLIDER_DOM_SELECTOR, @dom).slider "max", @sliderMax()
        if @filterMax() > val
          @filterMax val

    @filterRange.subscribe (val) =>
      try
        $(SLIDER_DOM_SELECTOR, @dom).slider "values", val

  generateSpec: () =>
    #### Generates the Polychart.js spec required for rendering
    #
    # :returns:
    #   A JSON object specifying the filter bounds. Contains information
    #   about metric name, and also ..
    #
    #   In the case of a numeric metric, the spec will look like
    #
    #     ge: <num ~ lowerbound>
    #     le: <num ~ upperbound>
    #
    #   When metric is a date type
    #
    #     ge: <unixdate>
    #     le: <unixdate>
    #     dateOptions: <string>
    #
    #   When metric is a categorical type
    #
    #     in: ["values", ...]
    #
    #   Finally, when there is either no filter or when the meta information for
    #   the filter is not obtained, then the object contains no additional
    #   information.

    if not @metaDone() then return null # No data to return

    spec = {}
    if @metric().type in ['date', 'num']
      values = $(SLIDER_DOM_SELECTOR, @dom).slider('values')
      if _.isNumber(values[0]) and values[0] != @sliderMin()
        spec.ge = values[0]
      if _.isNumber(values[1]) and values[1] != @sliderMax()
        spec.le = values[1]
      if @metric().type is 'date' and @dateOptionSelected()?
        spec.dateOptions = @dateOptionSelected()[0]
      if @notNull()
        spec.notnull = true
      else
        if not _.isEmpty(spec)
          spec.notnull = false
    else if @metric().type is "cat"
      if @filterCatValue().length > 0
        spec.in = @filterCatValue()
      else if @notNull()
        spec.notnull = true
    if not _.isEmpty(spec)
      spec.name = @metric().name
      spec.tableName = @metric().tableName
    spec

  initMetricItem: (metricDom, view) =>
    #### Initialization function called when KO template finishes rendering
    DND.makeDraggable(metricDom, view)
    @metric().attachDropdown(metricDom)
    @render()

  onMetricEnter: (event_, item) =>
    #### Initializs logic when new item enters (no async!)
    #
    # Initializes the bounds for filters, sets the possible options for
    # dropdowns and renders. The observable @metaDone is set to true upon
    # completion, signifying the presence of correct filter information.
    #
    # Params:
    #   :item: Object
    #     Object that must contain the following 'data' field.
    #
    #     data:
    #       type:      [cat|num|date]
    #       name:      "ColumnName"
    #       tableName: "TableName"
    #
    if @metaDone() # Replacing old metric
      @onMetricDiscard false, item
      return
    m = new DropdownMetricView(item.data, @label, 'tmpl-filter-dropdown', @)
    @metric(m)
    @tableMetaData.extendedMetaAsync m.columnInfo, (err, res) =>
      if err
        console.error err
        TOAST.raise "Error loading extended meta for table '#{m.tableName}'"
        return

      if @metric().type is 'cat'
        vals = _.map res.range.values, (v) -> v.toString()
        @filterCatOptions(vals)
      else
        @sliderMin(res.range.min); @filterMin(res.range.min)
        @sliderMax(res.range.max); @filterMax(res.range.max)

      @_defaults = _.extend @_defaults, res
      @metaDone(true)

  onMetricDiscard: (event, metricDom) =>
    #### Handler for metric leaving
    #
    # Run to clear the filter or replace the filter with a new one if
    # the old is being replaced in place.
    #
    # :params:
    #   :event:
    #     A jQuery event object passed on by the template. In the case that the
    #     event is `null`, the function has been called internally and signfies
    #     that the metric present was replaced by a new metric.
    #
    #   :metricDom:
    #     If this function is called by jQuery, then this is the DOM element
    #     holding the metric. If this function is called internally, this contains
    #     the item information for the new metric.
    #
    @metric().close()
    Events.ui.filter.remove.triggerElem @, (if not event then metricDom)
    @render()

  dropFilter: (dom) =>
    #### Determine whether or not to render dropdown
    $(dom).data('dnd-data').meta.type in ['date', 'num', 'cat']

  initSliderFilter: (@dom) =>
    #### Function to initialize jQuery slider; called by KO template
    slider = $(SLIDER_DOM_SELECTOR, @dom)
    if   @metaDone()          then @_makeSlider(slider)
    else @metaDone.subscribe () => @_makeSlider(slider)
    @notNull.subscribe () => @render()

  initCatFilter: (@dom) =>
    #### Function to initialize Dropdown menus; called by KO template
    @_setDefaults()
    @filterCatValue.subscribe () => @render()
    @notNull.subscribe () => @render()

  #### Helper functions

  _makeSlider: (slider) =>
    #### Function to initialize a JQuery slider.
    #
    #   Slider may be referred by $('.selector', @dom).slider(...)
    slider.slider(
      range: true
      max: @sliderMax()
      min: @sliderMin()
      values: @filterRange()
      slide: (evt, ui) =>
        @filterRange(ui.values)
        @render()
      change: (evt, ui) =>
        @filterRange(ui.values)
        @render()
    )
    @_setDefaults()

  _setDefaults: () =>
    #### Sets the default values of filters; implicitly takes @_defaults
    @filterMin(@sliderMin())
    @filterMax(@sliderMax())
    if @_defaults.dateOptions
      opt = @_defaults.dateOptions
      if _.isArray(opt) then opt = opt[0] # Old format
      if opt of DATE_FUNCTIONS and opt isnt "Custom"
        @dateOptionSelected([opt, DATE_FUNCTIONS[opt]])
      else if opt is "Custom"
        if @_defaults.le?
          @filterMax(+@_defaults.le)
        if @_defaults.ge?
          @filterMin(+@_defaults.ge)
    if _.isArray(@_defaults.in)
      @filterCatValue(@_defaults.in)
    if @_defaults.le?
      @filterMax(+@_defaults.le)
    if @_defaults.ge?
      @filterMin(+@_defaults.ge)

    @render()

  _render: () =>
    #### Helper for rendering; render if and only if meta is collected.
    if   @metaDone()          then Events.ui.chart.render.trigger()
    else @metaDone.subscribe () => @_render()

module.exports = FiltersView
