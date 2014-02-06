DashItem = require('poly/main/dash/item/base')
Events   = require('poly/main/events')

CONST    = require('poly/main/const')

class TextItem extends DashItem
  constructor: (@textContent, position={}, @defaultText='Type here...') ->
    unless ko.isObservable(@textContent)
      @textContent = ko.observable @textContent

    @templateName = 'tmpl-text-item' unless @templateName
    super(position)

  init: (@dom) =>
    super(dom)
    @loaded()

  onEditAreaBlur: ->
    Events.model.dashboarditem.update.trigger()

    return true

  serialize: (s={}) =>
    s.itemType = s.itemType ? 'TextItem'
    s.textContent = @textContent()
    super s

  deserialize: (s) =>
    @textContent(s.textContent) if s.textContent
    super(s)

module.exports = TextItem
