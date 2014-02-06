Aesthetic = require('poly/main/chart/aes/base')

class ColorAesthetic extends Aesthetic
  template: 'tmpl-aesthetic-color'
  constructor: (@aes, @name, @parent) ->
    super(@aes, @name, @parent)
    @selected = 'steelblue'
    @defaultValue = 'steelblue'
    @value = ko.observable(@defaultValue)
    @value.subscribe @render
  onMetricDiscard: (event, metricItem) =>
    @metric(null)
    @render()
    @afterRender(@dom)
  afterRender: (dom) =>
    @dom = dom
    simpleColor = $('.selector', dom)
    simpleColor.attr 'value', @value()
    simpleColor.simpleColor(
      cellWidth: 15
      cellHeight: 15
      boxWidth: 50
      boxHeight: 15
      border: 0
      columns: 9
    )
    simpleColor.bind 'change', (evt) =>
      @value evt.target.value
    $(".simpleColorContainer", dom).click () => false
  _setConstant: (spec) =>
    if spec.const
      @value(spec.const)
  _getConstant: () =>
    const: @value()

module.exports = ColorAesthetic
