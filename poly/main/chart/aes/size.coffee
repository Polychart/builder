Aesthetic = require('poly/main/chart/aes/base')

class SizeAesthetic extends Aesthetic
  template: 'tmpl-aesthetic-size'
  constructor: (@aes, @name, @parent) ->
    super(@aes, @name, @parent)
    @selected = 1
    @defaultValue = 2
    @value = ko.observable(@defaultValue)
    @value.subscribe @render
  onMetricDiscard: (event, metricItem) =>
    @metric(null)
    @render()
    @afterRender(@dom)
  afterRender: (dom) =>
    @dom = dom
    slider = $('.selector', dom)
    slider.slider(
      max: 10
      min:  1
      step: 1
      value: @value()
    )
    slider.bind 'slidechange', (evt, ui) =>
      @value(ui.value)
  _setConstant: (spec) =>
    if spec.const
      @value(spec.const)
  _getConstant: () =>
    const: @value()

module.exports = SizeAesthetic
