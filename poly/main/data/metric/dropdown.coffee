Events     = require('poly/main/events')
MetricView = require('poly/main/data/metric/base')

CONST      = require('poly/main/const')

class DropdownMetricView extends MetricView
  constructor: (columnInfo, @label, @dropdownTemplate, @dropdownData, @dropdownAfterRender) ->
    @toggleDropdown = _.throttle @_toggleDropdown # ..or clicks gets registerd 2x
    @dropdownShowing = false
    super(columnInfo)

  _toggleDropdown: =>
    if @name isnt 'count(*)'
      if @dropdownShowing
        Events.ui.dropdown.hide.trigger()
      else
        Events.ui.dropdown.show.trigger {
          templateName: @dropdownTemplate
          data: @dropdownData
          targetDom: @dom
          onRemove: @setInactive
          afterRender: @dropdownAfterRender
          info: {name: @label, value: @name}
        }

  setInactive: =>
    @dropdownShowing = false
    if @dom
      @dom.removeClass 'dropdown-active'
      @dom.draggable 'enable'

  close: =>
    Events.ui.dropdown.hide.trigger()

  attachDropdown: (dom) =>
    @dom = $(dom)
    Events.ui.dropdown.shown.onElem @dom, =>
      @dropdownShowing = true
      @dom.addClass 'dropdown-active'
      @dom.draggable 'disable'
    Events.ui.dropdown.hidden.onElem @dom, @setInactive

module.exports = DropdownMetricView
