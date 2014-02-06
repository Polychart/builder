###
Author : Jeeyoung Kim

Custom templating engine for knockout.

It uses the same templating syntax, except the templates can be provided
as a JSON string, instead of referring to the actual DOM elements.
###

StringTemplateEngine = (@templates) ->
  ###
  constructor for the String template engine.

  Notice that this class is not defined via coffeescript's "class" keyword,
  but the prototype is configured via ko.utils.extend...,
  this is because `StringTemplateEngine` primarily interacts with knockout code,
  which uses ko.utils.extend() internally.

  * templates - {String:String}
  ###
  @allowTemplateRewriting = false
  @templateCache = {} # {String:ObjectTemplateSource}

  # This return statement is required to have undefined as the return value.
  return

StringTemplateEngine.prototype = ko.utils.extend(new ko.nativeTemplateEngine(), {
  makeTemplateSource : (template) ->
    if typeof template == 'string'
      if @templates[template]
        # load from cache.
        if @templateCache[template]
          return @templateCache[template]
        return (@templateCache[template] = new ObjectTemplateSource(@templates[template]))
      else
        throw new Error("Unknown template type: " + template)
    # delegate to super.
    value = ko.nativeTemplateEngine.prototype.makeTemplateSource.apply(this, arguments)
    return value
})

class ObjectTemplateSource
  ###
  Implements the template source API that's defined internally inside Knockout.js
  ###
  constructor: (@template) ->
    @data = {}

  text: ->
    ###
    Getter / setter for text.
    ###
    if arguments.length == 0 then return @template
    @template = arguments[0]

  data: (key) ->
    ###
    Getter / setter for data
    ###
    if arguments.length == 1 then return @data[key]
    value = arguments[1]
    @data[key] = value

loadTemplateEngine = (templateDefinitions) ->
  ###
  Function to initialize knockout templates from strings.
  ###
  engine = new StringTemplateEngine(templateDefinitions)
  ko.setTemplateEngine engine

module.exports = {
  loadTemplateEngine : loadTemplateEngine
}
