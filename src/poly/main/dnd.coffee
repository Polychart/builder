###
Author : Jeeyoung Kim

Drag-and-drop related initialization code.

We're currently using JQuery UI's draggable. This is a wrapper around it, creating
our own set of events (defined under EVENTS object).

###

CONST          = require('poly/main/const')
Events         = require('poly/main/events')

CONTAINER_EXPR = '.dnd-panel'

########################################
# Names of events
EVENTS =
  ITEM_ENTER: 'dnd-item-enter'
  # ITEM_REMOVE: 'dnd-item-remove'
  ITEM_DISCARD: 'dnd-item-discard'

########################################
# Utility functions.
filterFunction = (evt, ui) ->
  targ = $(evt.target)
  data = targ.data('dnd-type')
  -> $(@).data('dnd-type') == data && (
    df = $(@).data('dnd-dropfilter')
    df or= -> true
    df targ
  )

makeEnterEvent = (item, itemData) ->
  dom : item
  data : itemData
  isDeleted : false
  delete : -> @isDeleted = true

makeRemoveEvent = (item, itemData) ->
  dom : item
  data : itemData

makeDiscardEvent = (item, itemData) ->
  dom : item
  data : itemData
  isDeleted : false
  delete : -> @isDeleted = true

handleError = (error) ->
  # Do not comment out this debugger statement, because it's the only
  # way to be notified of an error that's happening in draggable.
  debugger
  console.error(error, error.stack)

DRAGGABLE_EVENTS =
  ###
  Events used by initDraggable.
  Comment (Jeeyoung Kim)
  Unlike other places, this place need extensive try / catch statement.
  1. triggering various dnd events may cause exceptions in those event handlers.
  2. JQuery UI has silent catch-all statements that will prevent
  uncaught exception from propagating.
  Thus, uncaught exception in child event handler is forever lost.

  This logic does the following:
  1a. trigger ITEM_DISCARD if the item was thrown away from the panel.
  1b. trigger ITEM_ENTER if the item was moved to another panel.
  2.  trigger ITEM_REMOVE if the item was marked as deleted
      by the previous event handlers, by delete() method call.
  ###
  dispatchDndEvents: (evt, ui) ->
    try
      # This is the second thing that gets triggered on drop.
      item = $(@)
      newParent = item.data 'dnd-new-parent-dom'
      itemData = item.data 'dnd-data'
      dropPermitted = item.data 'dnd-drop-permitted'
      targetName = item.data 'dnd-drop-target-name'
      oldParent = item.parent()
      deleted = false
      if newParent
        if dropPermitted
          # Trigger entering event.
          enterEvt = makeEnterEvent item, itemData
          try
            newParent.trigger(EVENTS.ITEM_ENTER, enterEvt)
          finally deleted = enterEvt.isDeleted
        else
          Events.ui.dnd.reject.trigger info: target: targetName
      else
        Events.ui.dnd.drop.trigger info: target: null
    catch error then handleError(error)
    finally
      # If the item is deleted, then trigger the delete event.
      try
        if deleted or not newParent
          deleteEvt = makeRemoveEvent item, itemData
          oldParent.trigger(EVENTS.ITEM_DISCARD, deleteEvt)
      catch error then handleError(error)
      finally
        # reset dnd-new-parent-dom.
        item.data 'dnd-new-parent-dom', null
    return

  hlStart: (evt, ui) ->
    $(CONTAINER_EXPR).filter(filterFunction evt).addClass('highlight')
    Events.ui.highlight.begin.trigger selector: ".highlight:visible:not(.disabled)"
  hlStop: (evt, ui) ->
    $('.highlight').removeClass 'highlight'
    $('.highlight-strong').removeClass 'highlight-strong'
    Events.ui.highlight.end.trigger()
  increaseZIndex : (evt, ui) -> $(@).addClass 'item-selected'
  resetZIndex : (evt, ui) -> $(@).removeClass 'item-selected'
  hide: (evt, ui) -> $(@).css('visibility','hidden')
  show: (evt, ui) -> $(@).css('visibility','')

_commonOptions = ($obj, options) ->
  ###
  common options between initDraggable and initDroppable.
  ###
  {datatype} = options
  if datatype
    $obj.data('dnd-type', datatype)

initDraggable = ($obj, options) ->
  ###
  Turn the given DOM into draggable.

  * $obj - jQuery wrapper around target draggable object
  * options - optional parameteres
  * optiony.datatype - sets dnd-type
  ###
  options or= {}
  $obj.draggable(
    revert:true
    revertDuration:0
    containment:'document'
    appendTo:'body'
    helper: 'clone'
    scroll: false
  )
  _commonOptions($obj, options)

# unbind pre-existing dndDispatch events.
  $obj.unbind '.dndDispatch'

  $obj.on 'dragstart.dndDispatch', -> Events.ui.dnd.start.trigger info: name: options.name

  $obj.on 'dragstart.dndDispatch', DRAGGABLE_EVENTS.hlStart
  $obj.on 'dragstop.dndDispatch',  DRAGGABLE_EVENTS.hlStop

  $obj.on 'dragstop.dndDispatch',  DRAGGABLE_EVENTS.dispatchDndEvents

  $obj.on 'dragstart.dndDispatch', DRAGGABLE_EVENTS.increaseZIndex
  $obj.on 'dragstop.dndDispatch',  DRAGGABLE_EVENTS.resetZIndex
  $obj.on 'dragstart.dndDispatch', DRAGGABLE_EVENTS.hide
  $obj.on 'dragstop.dndDispatch',  DRAGGABLE_EVENTS.show

# event handlers used by initDroppable - outside the closure, because the closure is unnecessary.
initDroppable_accept = (dom) ->
  $(@).data('dnd-type') == dom.data('dnd-type')
initDroppable_over = ->
  $(@).addClass 'highlight-strong'
initDroppable_out = ->
  $(@).removeClass 'highlight-strong'

initDroppable = ($obj, options) =>
  ###
  Turn the given DOM into droppable.

  * options - optional parameteres
  * options.datatype - sets dnd-type
  * options.paneltype - sets dnd-panel-type
  * options.itementer - drop event handler.
  * options.itemdiscard - drop event handler.
  * options.dropfilter - drop acceptance filter
  ###

  options or= {}
  _commonOptions($obj, options)
  {datatype, paneltype, itementer, itemdiscard, dropfilter, name} = options

  dropfilter or= -> true

  $obj.data 'dnd-dropfilter', dropfilter

  $obj.droppable(
    accept: initDroppable_accept
    over : initDroppable_over
    out : initDroppable_out
    drop : (evt, ui) ->
      # This is the first thing that gets triggered on drop.
      # set the dnd-new-parent-dom data.
      item = $ ui.draggable
      dom = $ @
      newParent = item.data 'dnd-new-parent-dom', dom
      item.data 'dnd-drop-permitted', dropfilter item
      if name?
        item.data 'dnd-drop-target-name', name
  )
  $obj.addClass('dnd-panel')

  $obj.on EVENTS.ITEM_ENTER, -> Events.ui.dnd.drop.trigger info: target: name

  if paneltype
    $obj.data('dnd-panel-type', paneltype)
  if itementer
    $obj.bind(EVENTS.ITEM_ENTER, itementer)
  if itemdiscard
    $obj.bind(EVENTS.ITEM_DISCARD, itemdiscard)

cloneDraggable = ($obj) ->
  cloned = $obj.clone()
  for key in ['dnd-data', 'dnd-type']
    cloned.data key, $obj.data(key)
  return cloned

makeDraggable = (dom, metricItem) ->
  $dom = $(dom)
  $dom.data 'dnd-data', metricItem.columnInfo
  $dom.data 'dndMetricObj', metricItem # yes we do need it :(

  initDraggable $dom, datatype: 'metric', name: metricItem.name

module.exports = {
  CONTAINER_EXPR
  EVENTS
  cloneDraggable
  initDraggable
  initDroppable
  makeDraggable
}
