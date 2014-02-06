#### Internal modification of jQuery events
#
# Global event bus for Polychart. Basic facilities for analytics are included
# as well.
#
# Example usage:
#
#   Events.ui.chart.add.on (event, params) ->
#     ...
#
#   Events.ui.chart.add.trigger(params)
#
# where `params` is a JSON-object and `event` is a jQuery event object.
#
####

try
  serverApi = require('poly/common/serverApi')
catch err
  console.warn "Missing `serverApi` module, continuing without it."
  serverApi = null

class EventsFactoryConstructor
  #### Factory class for event trees
  #
  # Factory-like constructor for event trees. Given an event tree, this object
  # will provide methods for obtaining all or parts of an instantiated event
  # tree.
  #
  #  Constructor Params:
  #   _tree: Object
  #     This object is the uninstantiated event tree. The form of this is
  #     detailed in @getTreeFor.
  #
  #   _defaultPropHandler: Function(object, string) -> *
  #     A function which is invoked at the bottom of the event tree, with the
  #     values at the bottom as arguments. In otherwords, this function is
  #     called with the default properties set at each event-leaf node, along
  #     with the name of the bottom leaf node.
  #
  #  Public Methods:
  #   @getTree: Function() -> Object
  #     Gives the full instantiated event tree corresponding to the `@_tree`
  #     object initially passed in.
  #
  #   @getTreeFor: Function(String) -> Object
  #     Gives the subtree of the event tree whose top-level name is the value
  #     of the argument. If the uninstantiated event tree does not have a value
  #     corresponding to the input key, then the full tree is returned.
  #       For example, if the uninstantiated tree is
  #
  #         @_tree = page1:
  #                    object1:
  #                     ...
  #                    ...
  #                  page2:
  #                  ...
  #
  #     and one calls `EventsFactory.getTreeFor('page1')`, then the event
  #     subtree for `page1` is returned. However, if one calls
  #     `EventsFactory.getTreeFor('object1)' and there is no top-level key of
  #     `object1`, then the full tree is returned.
  #
  constructor: () ->
    @evtHistory        = {}
    @_tree             = null
    @_dummy            = $({})
    @_defaultListeners = {}

  getTree: (tree, defaultPropHandler) =>
    #### Gives the full event tree
    @getTreeFor tree, defaultPropHandler, null

  getTreeFor: (@tree, @defaultPropHandler, page) =>
    #### Gives specific toplevel subtree.
    #
    # If the argument `page` is given, and `page` is a top level key for
    # the given event tree, then the subtree corresponding to `page` is
    # returned. Otherwise, the full tree is returned.
    #
    # Params:
    #   page: String
    #     The string corresponding to a key in the uninstantiated event
    #     tree parameter @_tree. This is optional.
    #
    # Returns: Object
    #   If `page` is given and found in @_tree, then the subtree in @_tree
    #   will be returned; otherwise, the full, instantiated event tree will
    #   be returned.
    #
    unless _.isFunction @defaultPropHandler
      @defaultPropHandler = ->
    if page? and @_tree? and page of @_tree
      return @_tree[page]
    else if page? and page of @tree
      return @_instantiateTree @tree[page], null
    else
      @_tree = @_instantiateTree @tree, null
      return @_tree

  addEventTrackingTo: (elem, evt, type, info) =>
    #### Add event tracking to specific elements
    #
    # Params:
    #   elem: jQuery DOM Element
    #     The DOM element on which an event should be attached to.
    #
    #   evt: EventLeaf node
    #     An event from the instantiated event tree that is to be attached
    #     to the given element.
    #
    #   type: String
    #     A string denoting the type of event that is to be added. This is
    #     passed to whatever analytics engine that is running as "track#{type}".
    #
    #   info: Object
    #     Additional information that is to be passed to the analytics engine
    #     when this event is fired.
    #
    # Returns: void
    #   This method is called to attach a specific event.
    #
    if info? and not _.isObject info
      info = info: "#{info}"

    _debug "analytics.track#{type}", elem, evt.name, info
    if window.analytics?
      analytics["track#{type}"] elem, evt.name, info

  _instantiateTree: (tree, name) ->
    #### Given a tree-structure, makes an event tree
    #
    # This function recursively walks down the tree and populates an object
    # returns a tree whose leaves are event nodes. Leaves are considered objets
    # whose values have non-object values---that is to say, the lowest level is
    # that which contains an object of settings.
    #
    #  Params
    #    tree: Object
    #     The uninstantiated object-tree that is to be made into the full event
    #     tree. The parameter `tree` should look as follows
    #
    #       topLevelName:
    #         subLevelName:
    #           ... (however many subdivisions of levels)
    #             action1:
    #               defaultProperty1: value1
    #               defaultProperty2: value2
    #               ...
    #             ...
    #     Above, the values of the object corresponding to `action1` are
    #     non-object values, and so the node `action1` is considered a leaf.
    #
    #    name: String
    #     This string is used to name the node. The name is recursively set,
    #     with the key of each layer of the tree separated by an '_'. For
    #     example, the name at `action1` above would be
    #
    #       "topLevelName_subLevelName_(...)_action1"
    #
    #  Return: Object
    #   The object returned by this function will be similar in structure as
    #   the input event tree, except the leaf nodes will have properties defined
    #   in EventLeaf.
    #
    result = {}
    for key, val of tree
      newName = if name? then "#{name}_#{key}" else key
      # Bottom of tree, since lowest object is default properties
      twoDown = _.values(_.values(tree)[0])
      if _.isEmpty(twoDown) or not _.isObject(twoDown[0]) or _.isArray(twoDown[0])
        result[key] = new EventLeaf(newName, val)
        @defaultPropHandler newName, val
      else
        result[key] = @_instantiateTree(val, newName)
    return result

  _registerDefaultListeners: () ->
    #### Registers default listeners onto a dummy object
    _.each @_defaultListeners, (listener, evt) ->
      @_dummy.on evt, listener
    return

  #### Helper methods for event history

  _getHistory: (id) ->
    if id?
      @evtHistory[id]
    else
      @evtHistory

  _setHistory: (key, val) ->
    if key? and val?
      @evtHistory[key] = val
    return

  #### Helper functions to define methods for Event leaves

  _on: (evt, sel, dat, fn) =>
    _debug "on", evt, sel, dat, fn
    @_dummy.on evt, sel, dat, fn

  _one: (evt, sel, dat, fn) =>
    _debug "one", evt, sel, dat, fn
    @_dummy.one evt, sel, dat, fn

  _trigger: (evt, pars) =>
    _debug "trigger", evt, pars
    id              = _generateId()
    @_setHistory evt, id
    @_dummy.trigger evt, _.extend({}, pars, cid: id)

  _chain: (evt, prev, pars) =>
    _debug "chain", evt, prev, pars

    id = prev ? generateId()
    unless _.isNumber id # Then id is an event
      if id?.name? then id = id.name
      id = @_getHistory id
    @_dummy.trigger evt, _.extend({}, pars, cid: id)

  ## Tracking Event Helpers

  _trackClick: (str, obj, pars) ->
    $(obj).click (evt) =>
      @_track str, pars

  _trackForm: (str, obj, pars) ->
    $(obj).submit (evt) =>
      evt.preventDefault()
      @_track str, pars
      setTimeout ->
        $(obj).submit()
      , 500 # this is bad, it should be waiting for a response to the tracking

  _trackLink: (str, obj, pars) ->
    href = $(obj).attr 'href'
    $(obj).click (evt) =>
      evt.preventDefault()
      @_track str, pars
      setTimeout ->
        window.location.href = href
      , 500 # this is bad, it should be waiting for a response to the tracking

  ## Analytics Event Helpers

  _identify: (e, t, n, r) ->
    _debug "analytics.identify", e, t, n, r
    if window.analytics?
      window.analytics.identify e, t, n, r

  _track: (e, t, n, r) ->
    _debug "analytics.track", e, t, n, r
    if window.analytics?
      window.analytics.track e, t, n, r
      if serverApi? then serverApi.sendPost "/event/#{e}", t

EventsFactory = new EventsFactoryConstructor()

class EventLeaf
  #### Object representing a concrete event

  constructor: (@name, @defaults) ->

  #### General events

  on: (sel, dat, fn) =>
    EventsFactory._on @name, sel, dat, fn

  one: (sel, dat, fn) =>
    EventsFactory._one @name, sel, dat, fn

  trigger: (pars) =>
    EventsFactory._trigger @name, pars

  chain: (prev, pars) =>
    EventsFactory._chain @name, prev, pars

  #### Action tracking events

  trackClick: (obj, pars) =>
    EventsFactory._trackClick @name, obj, pars

  trackForm: (obj, pars) =>
    EventsFactory._trackForm @name, obj, pars

  trackLink: (obj, pars) =>
    EventsFactory._trackLink @name, obj, pars

  #### Object specific events

  onElem: (obj, sel, dat, fn) =>
    $(obj).on @name, sel, dat, fn

  oneElem: (obj, sel, dat, fn) =>
    $(obj).one @name, sel, dat, fn

  triggerElem: (obj, pars) =>
    $(obj).trigger @name, pars

#### Helper functions for Events

_generateId = -> "#{Math.random()}"

_debug = (funString, args...) ->
  #### Helper to emit debug messages
  #
  # This function will emit messages into the debug console if the flag
  # window.polydebug or the cookie 'polydebug' is set.
  #
  #  Params:
  #    funString: String
  #     This string will wrap the other arguments. For example,
  #
  #       funString(arg1, arg2, ...)
  #
  #    args: Array
  #     Array that shall contain the arguments passed to either funString or
  #     errString.
  #
  #  Returns: void
  #   Helper to emit messages into debug.
  #
  if window.polydebug or Cookies.read('polydebug')
    try
      argList = (_.map args, JSON.stringify).join(', ')
      console.debug "#{funString}(#{argList})"
    catch err
      console.debug "#{funString}(#{args.join(', ')})"
      console.debug "While attempting to stringfy previous: #{err}"
      window.errObj = args
  return

module.exports = EventsFactory
