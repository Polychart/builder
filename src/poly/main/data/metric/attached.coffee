CONST              = require('poly/main/const')
TOAST              = require('poly/main/error/toast')
DropdownMetricView = require('poly/main/data/metric/dropdown')
Events             = require('poly/main/events')

###
# A note on metric names:
#
# titleName   : what to refer to the metric on the actual chart
# name        : original name or alias associated with the col (no bin/stats)
# visibleName : the name to display on metric (has bin/stat info)
# formula     : what name/formula to send to polyjs (no bin/stats)
# fullFormula*: name/formula to send to polyjs (has bin/stats info)
#    * currently only in generateSpec() function
###

class AttachedMetricView extends DropdownMetricView
  # PARAMETERS
  #  @columnInfo - a column info object
  #  @label - label for the metric specifying the role it is playing
  #  @updateFn - function to call whenever metric is updated, e.g. to redraw
  #  @options - the layer-aesthetics options & defaults, as in CONST.layer
  #  @attachedMetrics - observable of other metrics in the layer (for sorting)
  #  @defaults - if this metric is reconstructed, initial sorting & stats
  constructor: (columnInfo, label, updateFn, @options, attachedMetrics, defaults={}) ->
    super(columnInfo, label, 'tmpl-metric-option', @)

    @removeText ?= "Remove \"" + @name + "\" from " + @label
    # Name for TITLING the chart
    @titleName = @name
    # NOTE: @columnInfo.meta.type overrides params.type, if any
    @type = @columnInfo.meta.type
    if not @type
      TOAST.raise("Metadata does not contain type for metric #{@name}")
    # more options
    @sortMetricList = ko.computed () =>
      keys = ["None"]
      for m in attachedMetrics()
        if m isnt @
          if m.fullName? # only metrics that are of class AttachedMetricsView
            keys.push(m)
      _.uniq keys
    @sortMetricOptionText = (m) -> if m is "None" then "None" else m.fullName()

    @sortMetric = ko.observable("None")
    if defaults.sort?
      for m in attachedMetrics()
        if m isnt @ and m.fullName? and defaults.sortName? and (m.fullName() is defaults.sortName)
          @sortMetric(m)
          break

    @asc = ko.observable(defaults.asc ? 'asc')

    @statsList = ko.computed () => @options().stat[@type]
    @statsDefault = ko.computed () =>
      if @name isnt 'count(*)'
        @options().defaultStat[@type]
      else
        'None'
    @stats = ko.observable(defaults.stats ? @statsDefault())

    @binwidth = ko.observable(defaults.bin ?
      if @name is 'count(*)'
        null
      else if @type is 'num'
        defaults.bin ? 1
      else if @type is 'date'
        if @columnInfo.meta.timerange? then @columnInfo.meta.timerange else 'day'
      else
        null
    )
    @binoptional = ko.computed () => !@options().bin
    @binned = ko.observable(defaults.bin || @options().bin) # might be changed
    @binned.subscribe updateFn

    @binoptional.subscribe (val) =>
      if !val
        @binned(true) # force binning
        if not (@binwidth()?)
          if @type is 'num'
            defaults.bin ? 1
          else if @type is 'date'
            if @columnInfo.meta.timerange? then @columnInfo.meta.timerange else 'month'

    @visibleName = ko.computed () => @_statName @name
    @fullName    = ko.computed () =>
      if @name is 'count(*)'
        @name
      else
        @_statName "#{@tableName}.#{@name}"

    @binwidth.subscribe updateFn
    @stats.subscribe updateFn
    @sortMetric.subscribe updateFn
    @asc.subscribe updateFn
    @statsList.subscribe (newAcceptableVals) =>
      # in case a statistic changes...
      if not (@stats() in newAcceptableVals)
        @stats(@statsDefault())
    @sortMetricList.subscribe (newValues) =>
      if not (@sortMetric() in newValues)
        @sortMetric(newValues[0])

  fullMeta: () =>
    moreMeta = {}
    if @binned() and @binwidth()
      moreMeta.bw = @binwidth()
    if @type is 'date'
      moreMeta.format = 'unix'
    _.extend @columnInfo.meta, moreMeta

  _statName: (name) =>
    if @stats() isnt 'None'
      "#{CONST.stats.nameToStat[@stats()]}(#{name})"
    else if @binned() and @binwidth()
      if @type is 'num'
        "bin(#{name},#{@binwidth()})"
      else
        "bin(#{name},\"#{@binwidth()}\")"
    else
      name

  initSlider: (dom) =>
    if not _.isFunction(@sliderVal)
      @sliderVal = ko.observable(if @binwidth then 'binwidth' else 'default')
    if @type == 'num'
      @initNumSlider(dom)
    if @type == 'date'
      @initDateSlider(dom)

  initNumSlider: (dom) =>
    if @sliderVal() is 'default' then @sliderVal(0)
    else @sliderVal(Math.log(@binwidth())/Math.LN10)
    slider = $('.selector', dom)
    slider.slider(
      max: 5
      min:  -3
      step: 1
      value: @sliderVal()
      slide: (evt, ui) =>
        @sliderVal ui.value
        @binwidth(Math.pow(10, @sliderVal()))
    )

  initDateSlider: (dom) =>
    TIMERANGE = ['second','minute','hour','day','week','month','twomonth','quarter','sixmonth','year', 'twoyear', 'fiveyear', 'decade']
    if /ga-(?:dimension|metric)-.*/.exec(@tableName)?
      TIMERANGE = TIMERANGE.slice(3)
    if @sliderVal() is 'default' then @sliderVal(4)
    else @sliderVal(TIMERANGE.indexOf(@binwidth()))
    slider = $('.selector', dom)
    slider.slider(
      max: TIMERANGE.length - 1
      min: 0
      step: 1
      value: @sliderVal()
      slide: (evt, ui) =>
        @sliderVal ui.value
        @binwidth(TIMERANGE[@sliderVal()])
    )

  toggleAsc: () =>
    if @asc() == 'asc'
      @asc('dsc')
    else
      @asc('asc')

  fullFormula: (tableMetaData, unbracket=false) =>
    f = @_statName @columnInfo.getFormula(tableMetaData, false)
    if unbracket
      polyjs.parser.unbracket f
    else
      f

  generateSpec: (tableMetaData) =>
    # get the full "formula" for polyjs, including binning & stats
    # note: for now we are removing '[' and ']' while the polyjs parser isnt
    #       yet updated
    spec =
      var: @fullFormula(tableMetaData, false)
      name: @name
      tableName: @tableName
      bin: @binwidth()
      stats: @stats()
    if @sortMetric() isnt 'None' and @sortMetric()
      spec.sort = @sortMetric().fullFormula(tableMetaData, false)
      spec.sortName = @sortMetric().fullName()
      spec.asc = @asc() == 'asc'
    spec

  discard: () =>
    @close()
    Events.ui.metric.remove.triggerElem @, elem: @

module.exports = AttachedMetricView
