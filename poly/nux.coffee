Events = require('poly/main/events')

class NuxView
  constructor: ({@steps, @onSkip}) ->
    @curStep = 0
    @arrowDir = ko.observable('left')
    @title = ko.observable()
    @msgs = ko.observable()
    @covers = ko.observableArray([])
    @instrPos = ko.observable({})
    @instructions = ko.observableArray([])
    @buttonText = ko.observable()
    @skippable = ko.observable false

    _.delay @nextStep, 100

  nextStep: () =>
    if @steps[@curStep]?.onFinish
      @steps[@curStep].onFinish()
    if @curStep == @steps.length
      @clear()
      return

    $('#nux-fade').remove()
    fader = $('#nux').clone()
    fader.attr('id', 'nux-fade')
    $('BODY').append(fader)

    fader.fadeOut()
    $('#nux').hide()

    _.delay () =>
      @_nextStep()
      $('#nux').fadeIn()
    , 500

  _nextStep: () =>
    step = @steps[@curStep]
    @curStep += 1
    @title(step.title)
    step.msgs = [step.msgs] if !_.isArray(step.msgs)
    @msgs(step.msgs)

    $ref = $(step.ref)
    @instrPos(
      top: ($ref.offset().top + step.top) + "px"
      left: ($ref.offset().left + step.left) + "px"
    )
    @arrowDir(step.arrowDir ? 'none')

    coverables = $(step.cover)
    @covers.removeAll()
    _.each coverables, (ele) =>
      $ele = $(ele)
      cover =
        top: $ele.offset().top + "px"
        left: $ele.offset().left + "px"
        width: $ele.outerWidth() + "px"
        height: $ele.outerHeight() + "px"
      @covers.push cover

    @instrComplete = 0
    @instructions.removeAll()

    step.instructions ?= []
    _.each step.instructions, (instr, idx) =>
      obj =
        i: idx+1
        strike: ko.observable(false)
      $.extend(obj, instr)
      @instructions.push obj
    if step.instructions.length > 0
      instr = @instructions()[@instrComplete]
      fn = (event, params) =>
        instr.strike(true)
        if ++@instrComplete == step.instructions.length
          _.delay @nextStep, 100
        else
          instr = @instructions()[@instrComplete]
          instr.event.one(fn)
      instr.event.one(fn)

    @buttonText step.buttonText

    @skippable step.skippable?

    if step.event
      step.event.one (event, params) =>
        @nextStep()

  clear: () =>
    $('#nux').fadeOut()

  skip: () =>
    @onSkip() if @onSkip
    @clear()

module.exports = NuxView
