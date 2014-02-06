###
# Class defining the qualities shared by the Chartbuilder, Tablebuilder, and
# Numeralbuilder.
###
Events = require('poly/main/events')
TOAST  = require('poly/main/error/toast')

EDIT_BOX_PADDING = 3

class Builder
  constructor: (@tableMetaData) ->
    @backButtonVisible = ko.observable(true)
    @render = _.debounce(@_render, 300) # Assumes that a _render method is defined.
    Events.ui.chart.render.on @render

  backToDashboard: (event) =>
    #### UI function for buttons.
    Events.ui.backtodbb.click.trigger from: @item

  serialize: () =>
    #### Serialization method for builders; always delete data and DOM reference
    spec = $.extend(true, {}, @spec)
    delete spec.dom
    delete spec.data
    spec

  loaded: (err) =>
    #### Helper function that is passed into Polychart2.js as a callback
    if err
      console.error err
      TOAST.raise err.message
      @loadingAnim.stopOnImage('/static/main/images/broken_chart.svg')
    else
      @loadingAnim.remove()

  initDom: (dom) =>
    #### Initialize the DOM on load; sets listeners and initial render.
    @dom = $(dom)[0]
    @_addListeners()
    @render()


  #### Helpers for setting up the render DOM


  _addEventListener: (type, handler) =>
    #### Helper to add an event listener to the DOM on which Polychart2.js renders.
    @dom.addEventListener type, handler, false

  _editTitle: (e, title, rotated=false) ->
    #### Method to fake editting text on the rendered charts/numerals
    #
    # This method handles UI for editting the title for charts
    # and numerals, and chart axes. This is done by positioning
    # a contenteditable box atop of the target text. The user
    # inputs the desired text, which is captured and placed into
    # the underlying Polychart2.js spec.
    obj     = e.detail.data
    editBox = $("<div contenteditable='true'>#{obj.node.textContent}</div>")
    $(@dom).append editBox
    obj.hide()

    #### Construct floating box
    for key, val of obj.attrs
      editBox.css key, val

    titleBBox = e.detail.data.getBBox()
    domOffset = $(@dom).offset()
    editBox.css
      left: domOffset.left + titleBBox.x - EDIT_BOX_PADDING
      top: domOffset.top + titleBBox.y - EDIT_BOX_PADDING
      position: 'fixed'
      'z-index': 9999999
      padding: "#{EDIT_BOX_PADDING}px"
    if rotated
      editBox.addClass "rotated"
      editBox.css top: domOffset.top + titleBBox.y + editBox.width() + EDIT_BOX_PADDING

    #### Set handlers for events
    editBox.on 'keydown', (evt) ->
      if evt.keyCode in [13, 27] # [enter, escape]
        editBox.blur()
        evt.preventDefault()

    editBox.on 'focus', () ->
      range = document.createRange()
      range.selectNodeContents editBox[0]
      sel = window.getSelection()
      sel.removeAllRanges()
      sel.addRange range

    editBox.on 'blur', (evt) ->
      newTitle = editBox.html()
      brIndex = newTitle.indexOf "<br>"
      if brIndex isnt -1
        newTitle = newTitle.slice 0, brIndex
      if newTitle is "" then newTitle = null
      title newTitle
      unless newTitle is null
        Events.ui.title.add.trigger()
        obj.attr text: newTitle
        obj.show()
      editBox.remove()

    editBox.focus()
    return

  _addTitleGlow: (jsObj) ->
    #### Helper to add label glows
    #
    # The argument `jsObj` is an object representing a fully
    # constructed Polychart2.js object. A glow handler is then attached to this
    # object.
    if not jsObj? then return

    jsObj.addHandler (type, obj, evt, graph) ->
      if type is 'tover' or \
         type is 'gover' and obj.type is 'text' and obj.evtData?
        obj.shadow = obj.clone().attr({fill: 'steelblue', opacity: 0.7})\
                                .insertBefore(obj)
        obj.shadow.blur(1)
        obj.attr cursor: if 'transform' of obj.attrs then 'vertical-text' else 'text'
      else if type is 'tout' or \
              type is 'gout' and obj.type is 'text' and obj.evtData?
        obj.shadow.remove()
    return

  _addListeners: ->
    #### Stub to attach listeners onto the rendering DOM

module.exports = Builder
