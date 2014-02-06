TextItem = require('poly/main/dash/item/text')

CONST    = require('poly/main/const')

class CommentItem extends TextItem
  constructor: (@author, value, position={}) ->
    @author or= PAGE_VARIABLE?.USERNAME ? ''
    position.width or= 5
    position.height or= 7

    @minWidth = 5
    @minHeight = 5

    @templateName = 'tmpl-comment-item' unless @templateName
    super(value, position, 'Write a comment here...')

    @shiftedZIndex = ko.computed =>
      1000000 + @zIndex()

  serialize: (s={}) =>
    s.author = @author
    s.itemType = "CommentItem"
    super s

  deserialize: (s) =>
    @author = s.author if s.author
    super(s)

module.exports = CommentItem
