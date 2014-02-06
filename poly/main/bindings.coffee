###
custom KO bindings.
Refer to [Custom Bindings](http://knockoutjs.com/documentation/custom-bindings.html)
for the instructions.
###

dnd    = require('poly/main/dnd')
CONST  = require('poly/main/const')
Events = require('poly/main/events')

unwrap = ko.utils.unwrapObservable
wrap = (x) ->
  if ko.isObservable x
    x
  else
    ko.observable x
peek = (x) ->
  if ko.isObservable x
    x.peek()
  else
    x


###
pui_dndContainer
----------------
This binding is used to make an element accept dragged elements using jQueryUI's
draggable/droppable functionality. It relies largely on the `initDroppable`
function implemented in `dnd.coffee` to apply the actual classes and invoke the
jQueryUI methods, and most options are passed through to this function. However,
this method does add the additional feature that, if a droppable object is
clicked, all draggables that would be accepted are highlighted. Clicking on one
of these highlighted draggables will behave as if the user had dragged it to
this droppable.

This should be bound to a configuration object containing the following options:
  * `datatype`: `string`
    The type of draggable this element should accept. This allows preliminary
    filtering to permit several sets of draggables and droppables to coexist.
    This option is passed to `dnd.initDroppable` and is not used directly.
  * `paneltype`: `string` *(optional)*
    This option is passed to `dnd.initDroppable` and is not used directly. The
    documenter does not understand what this option does, and it is not
    currently used.
  * `itementer`: `function(event, {element, data})`
    This function will be called when a draggable is dropped on this element (or
    clicked as described above). It is also passed to `dnd.initDroppable`.
  * `itemdiscard`: `function(event, {element, data})`
    This function will be called when a draggable that has previously been
    dropped on this element is discarded by dragging away. It is not used
    directly.
  * `dropfilter`: `function(element) -> bool`
    This function will be called to determine whether or not a specific
    draggable element should be accepted by this droppable. It is used to
    prevent triggering the `itementer` function and to avoid highlighting
    unacceptable draggables.
  * `name`: `string`
    A human-readable name describing this specific droppable. This is only for
    analytics purposes, and has no effect if analytics/event tracking is not
    enabled.
  * `rerender`: `ko.observable` *(optional)*
    A Knockout observable that can be subscribed to. When this observable is
    changed, the droppable code will be triggered again. This is used to
    re-attach events when the DOM will inevitably be updated by Knockout.
###
pui_dndContainer = {
  init: (element, valueAccessor) ->
    view = valueAccessor()
    {datatype, paneltype, itementer, itemdiscard, dropfilter, name, rerender} = view
    dropfilter or= -> true
    options = {datatype, paneltype, itementer, itemdiscard, dropfilter, name}
    (dnd.initDroppable $(element), options)

    initDroppableClick = () =>
      $('.droppable', element).click () =>
        Events.ui.dnd.selectdroppable.trigger info: target: name
        $('.table-metric-list.selected .metric').filter(-> dropfilter @).addClass 'highlight'
        Events.ui.highlight.begin.trigger {
          selector: '.highlight:visible:not(.disabled)'
          click: (event, $target) =>
            if dropfilter $target
              Events.ui.dnd.selectdraggable.trigger info: name: $target.data('dnd-data').name
              itementer event,
                dom: $target
                data: $target.data 'dnd-data'
        }
    _.defer initDroppableClick # Defer until templates render

    if rerender
      rerender.subscribe () => _.defer initDroppableClick
}


###
Dropdown
--------
A basic object containing Knockout.js binding code for custom dropdown menus.

See DropdownSingle and DropdownMulti for example of use.
###
Dropdown =
  update: (dropdownType, element, valueAccessor) ->
    {selected, options, optionsText, hasIcons} = Dropdown.unwrap valueAccessor
    dropdownType.setData(element, selected, options, hasIcons, optionsText)
    return

  initElement: (element, isDropdownVisible, templateName, childTemplate, name) ->
    $element = $(element)

    Events.ui.dropdown.shown.onElem $element, ->
      isDropdownVisible true
      $element.addClass 'dropdown-active'
      $element.removeClass 'dropdown-inactive'
    Events.ui.dropdown.hidden.onElem $element, ->
      isDropdownVisible false
      $element.removeClass 'dropdown-active'
      $element.addClass 'dropdown-inactive'

    clickHandler = ->
      if isDropdownVisible()
        Events.ui.dropdown.hide.trigger targetDom: $element
      else
        optionsData = $element.data "optionsData"
        Events.ui.dropdown.show.trigger
          targetDom: $element
          data: options: optionsData
          templateName: templateName
          info: name: name
    $element.click _.throttle(clickHandler)

    $element.addClass 'dropdown-inactive'
    ko.applyBindingsToNode element, childTemplate
    return

  unwrap: (valueAccessor) ->
    value = ko.utils.unwrapObservable valueAccessor()
    {selected, options, optionsText, hasIcons, name} = value
    if ko.isObservable(options)
      options = options()
    {selected, options, optionsText, hasIcons, name}


###
DropdownSingle
--------------
This is a variant of the Dropdown object which permits a single entry to be
selected. The options parameter is to be given as an array of arrays. The inner
arrays represent name-value pairs:

      options = [ ["Name 1", "Value 1"]
                  ["Name 2", "Value 2"]
                  ...
                ]

For convenience, if one passes in a flat array like

      options = [ "Value 1", "Value 2", ... ]

then this will be internally converted to the above form, where both name and
value take on the value given.

One option that may be specified for DropdownSingle is whether or not each
option has an icon. This is specified via the option 'hasIcon' whilst declaring
the template bit. By default, the icon is found via the CSS class
'img-icon-#{value}'. In the case that a custom name is needed for the icon, a
third element may be put in the array and that will be used in place of value.
###
DropdownSingle =
  template: 'tmpl-dropdown-single-menu'

  init: (element, valueAccessor) ->
    {selected, options, optionsText, hasIcons, name} = Dropdown.unwrap valueAccessor
    isDropdownVisible = ko.observable(false)
    childTemplate = template:
      name: if hasIcons then 'tmpl-dropdown' else 'tmpl-dropdown-no-icon',

    Dropdown.initElement element, isDropdownVisible, DropdownSingle.template, childTemplate, name
    selected.subscribe () ->
      DropdownSingle.handleDropdownChange element, selected(), name
    DropdownSingle.setData(element, selected, options, hasIcons)
    DropdownSingle.handleDropdownChange element, selected(), name
    return

  update: (element, valueAccessor) ->
    Dropdown.update DropdownSingle, element, valueAccessor
    return

  handleDropdownChange: (element, selected, name) ->
    $('.select-icon', element).attr 'class', "select-icon img-icon-#{selected[selected.length - 1]}"
    $('.name', element).html selected[0]
    Events.ui.dropdown.hide.trigger targetDom: $(element)
    Events.ui.dropdown.choose.trigger info: {name: name, value: selected[1]}
    return

  setData: (element, selected, options, hasIcons, optionsText=(v)->v) ->
    if options? and not _.isArray(options[0])
      options = _.zip options, options

    optionsData = _.map options, (o) =>
      if o.length > 3 || !_.isString(o[0])
        throw "DropdownSingle options must be an array of the form [[\"Name 1\", value], [\"Name 2\", value]]"

      iconClass: if hasIcons then "select-icon img-icon-#{o[o.length - 1]}" else null
      text:     optionsText(o[0])
      value:    o[1]
      selected: selected
      handler:  => selected o

    $(element).data "optionsData", optionsData
    return


###
DropdownMulti
-------------
This is a variant of the Dropdown class which allows for easy mutliselect.
The expected data format for the options is an array of objects with the fields
'field' and 'value':

    options = [ { field: "Name 1", value: "Value 1"}
                { field: "Name 2", value: "Value 2"}
                ...
              ]
For convenience, if the options array is passed in as a flat array of values,

    options = ["Value 1", "Value 2", ... ]

then this will be converted to the required for, with both field and value
taking on the array item.
###
DropdownMulti =
  template: 'tmpl-dropdown-multi-menu'

  init: (element, valueAccessor) ->
    {selected, options, optionsText, name} = Dropdown.unwrap valueAccessor
    isDropdownVisible = ko.observable false
    childTemplate = template:
      name: 'tmpl-dropdown-no-icon'

    Dropdown.initElement element, isDropdownVisible, DropdownMulti.template, childTemplate, name
    selected.subscribe ->
      DropdownMulti.handleDropdownChange element, selected()
    DropdownMulti.setData(element, selected, options, optionsText)
    DropdownMulti.handleDropdownChange element, selected()
    return

  update: (element, valueAccessor) ->
    Dropdown.update DropdownMulti, element, valueAccessor
    return

  handleDropdownChange: (element, selected) ->
    $('.name', element).html("#{selected.length} item" + (if selected.length is 1 then " " else "s ") + "selected")
    return

  setData: (element, selected, options, hasIcon, optionsText=(v)->v) ->
    if options[0]? and not _.isObject(options[0])
      options = _.map options, (v) -> field: v, value: v
    optionsData = _.map options, (o) ->
      if 'field' not of o or 'value' not of o
        throw "DropdownMulti options must be an array with elements of the form {field: 'Name 1', value: 'Value 1'}"
      text:     optionsText(o.field)
      selected: selected().indexOf(o.value) isnt -1
      handler:  (ele, evt) ->
        _selected = selected()
        idx    = _selected.indexOf o.value
        if idx is -1
          $(evt.target).closest('.option').addClass('checked')
          _selected.push(o.value)
        else
          $(evt.target).closest('.option').removeClass('checked')
          _selected.splice(idx,1)
        selected _selected
    $(element).data "optionsData", optionsData
    return


###
pui_contentEditable
-------------------
Binding to enable contenteditable elements that play nicely with Knockout. This
should be bound to an observable containing the text content of the element. The
user's changes are reflected in the observable, and vice versa. It also has some
mildly insane logic to play nicely with `pui_jqDraggableResizeable`.

Adapted from
[a StackOverflow response](http://stackoverflow.com/questions/7904522/knockout-content-editable-custom-binding).

The following "helper" bindings also exist:
  * `pui_placeholder`: `string` *(optional)*
    This binding, if present, defines the placeholder text to be used when the
    element is unselected and has no content.
  * `pui_placeholder_class`: `string` *(optional)*
    This binding, if present, defines a class to be added to the element when
    the placeholder is shown.
  * `pui_draggableSelector`: `string` *(optional)*
    If present, this binding defines a selector that can be used to find an
    ancestor element that is draggable. This is used to make contenteditable
    elements work even when inside a draggable container. The selected container
    is expected to be using the `pui_jqDraggableResizeable` binding.
###
pui_contentEditable = {
  init: (element, valueAccessor, allBindingsAccessor) =>
    value = wrap valueAccessor()
    $elem = $(element)
    $elem.on 'keydown', (evt) ->
      if evt.keyCode in [13, 27] # [enter, escape]
        $elem.blur()
        evt.preventDefault()

    _onkeyup = () ->
      modelValue   = valueAccessor()
      elementValue = $elem.text()
      if ko.isWriteableObservable modelValue
        modelValue elementValue
      else
        allBindings = allBindingsAccessor()
        if allBindings['_ko_property_writers'] && allBindings['_ko_property_writers'].htmlValue
          allBindings['_ko_property_writers'].htmlValue elementValue
    $elem.on 'keyup', _.debounce(_onkeyup, 600)

    allBindings = allBindingsAccessor()

    # Default text which disappears when clicked
    placeholder      = wrap allBindings['pui_placeholder']
    placeholderClass = wrap allBindings['pui_placeholder_class']

    showPlaceholder = ko.observable !value()

    setTimeout -> # defer until KO has finished processing the bindings
      showPlaceholder !value()
      ko.computed ->
        phClass = placeholderClass()
        if phClass
          if showPlaceholder()
            $elem.addClass phClass
            $elem.html placeholder()
          else
            $elem.removeClass phClass
            $elem.html value()
    , 1

    # Support for dragging containers
    draggableSelector = wrap allBindings['pui_draggableSelector']

    $elem.on 'mouseover', ->
      $elem.addClass 'hover'

    $elem.on 'mouseout', ->
      $elem.removeClass 'hover'

    $elem.on 'click', (evt) ->
      if draggableSelector()?
        if $elem.closest(draggableSelector()).data 'pui-was-dragged'
          $elem.closest(draggableSelector()).data 'pui-was-dragged', false
          return
      showPlaceholder false
      if not value()
        setTimeout ->
          $elem.setCaret 0
          $elem.trigger 'focus'
        , 1
      else if not $elem.data 'pui-has-focus'
        $elem.trigger 'focus'
        $elem.setCaretFromPoint evt.pageX, evt.pageY
        $elem.data 'pui-has-focus', true
      if draggableSelector()?
        $elem.closest(draggableSelector()).draggable cancel: '*'

    $elem.on 'blur', =>
      value $elem.html()
      $elem.data 'pui-has-focus', false
      if not value()
        showPlaceholder true
      if draggableSelector()?
        $elem.closest(draggableSelector()).draggable cancel: null

  update: (element, valueAccessor, allBindingsAccessor) =>
    value = unwrap(valueAccessor()) || ''
    if element.innerHTML != value
      element.innerHTML = value
      allBindings = allBindingsAccessor()
}


###
SlickgridData
-------------
This binding is used to create and automatically update a SlickGrid table using
observable values. Two other "helper" bindings are also used:
`SlickgridColumns`, and `SlickgridHeaderTmpl`. Each of these bindings may be
given either a raw value or a Knockout observable.

The `SlickgridColumns` binding should be an array of objects representing some
properties of each column in the grid. These objects should contain two
fields: a `name` property, and a `field` property. Their values should be
strings, and may be wrapped in Knockout observables. `name` typically provides
the displayed column name, while `field` is used to index the column internally.
The column's `field` should be unique among all columns in this grid. Note that
while updating an observable `field` will cause the relevant sections of the
grid to re-render, `name` is explicitly not subscribed to and will not trigger a
re-render when changed. This permits custom headers to make the column name
editable without causing racy behaviour.

The `SlickgridHeaderTmpl` binding is optional. If provided, it should be a
string giving the name of a Knockout template to be rendered in each header cell
instead of the default SlickGrid header. The model object for each cell will be
the column object for that column (as given by the `SlickgridColumns` binding).
There are no restrictions on the fields and methods that a column object may
provide, apart from the required `name` and `field` properties.

The `SlickgridData` binding should be an array of objects. Each object
represents one row in the grid, and should contain one property for each column
(corresponding to the `field` property of that column).

Caveats of working with this binding:
  * The `SlickgridColumns` binding, if provided from a template, must be
    directly observable. It cannot be implicitly computed, as in the form
    `SlickgridColumns: myObservable().columns`, because it is not evaluated in
    a computed wrapper. Instead, the computed should be explicitly defined in
    the column model.
  * The `SlickgridHeaderTmpl` binding is not currently subscribed to, if it is
    an observable (explicit or implicit).
###
SlickgridData = {
  init: (element, valueAccessor, allBindingsAccessor) ->
    data = unwrap valueAccessor()
    allBindings = allBindingsAccessor()
    columns = allBindings.SlickgridColumns
    columnData = ko.computed ->
      {
        name: peek col.name
        field: unwrap col.field
        id: idx
      } for col, idx in unwrap columns
    headerTmpl = unwrap allBindings.SlickgridHeaderTmpl

    slickGrid = new Slick.Grid element, data, columnData(),
      enableCellNavigation: true
      enableColumnReorder: false

    if headerTmpl?
      slickGrid.onHeaderCellRendered.subscribe (e, {node, column: {id}}) ->
        headerDiv = $("<div>")
        ko.applyBindingsToNode headerDiv[0], template: {name: headerTmpl}, (unwrap columns)[id]
        $(node).empty().append headerDiv

    columnData.subscribe (val) ->
      slickGrid.setColumns val
      slickGrid.invalidate()

    $(element).data 'grid', slickGrid

  update: (element, valueAccessor, allBindingsAccessor) ->
    data = unwrap valueAccessor()

    slickGrid = $(element).data 'grid'
    slickGrid.setData data, true
    slickGrid.invalidate()
}


###
pui_jqDraggableResizeable
-------------------------
This binding uses jQueryUI's draggable and resizeable bindings to make charts
and other dashboard items interactive. It also contains some logic to work
better with `pui_contentEditable` items. The combined behaviour is a reasonable
combination: if the user clicks and drags, the item is dragged around. If he or
she clicks without dragging, the cursor is placed in the editable area as
normal. The logic to do this is... somewhat less reasonable.

This binding should be bound to a configuration object, optionally wrapped in a
Knockout observable. The configuration options are as follows:
  * `gridSize`: `number`
    The size of one square on the drag/resize grid, in pixels. Defaults to `1`.
  * `minWidth`, `minHeight`: `number` *(optional)*
    The minimum width and height, in grid units, of this element. Both default
    to `1`.
  * `gridTop`, `gridLeft`, `gridWidth`, `gridHeight`: `ko.observable(number)`
    Observables describing the position of this object in grid units. The values
    will be updated automatically as the user drags the element around. They
    will not be watched for changes after initialization.
  * `isDragging`, `isResizing`: `ko.observable(bool)` *(optional)*
    Observable flags for whether or not the current element is being dragged or
    resized. The flags are automatically set and unset as the user interacts.
    They will not be watched for changes after initialization.
  * `dragEnabled`, `resizeEnabled`: `ko.observable(bool)` *(optional)*
    Observable flags for whether or not the user may drag or resize this item.
###
pui_jqDraggableResizeable = {
  init: (element, valueAccessor) ->
    params = unwrap valueAccessor()
    {
      gridSize
      minWidth
      minHeight
      gridTop
      gridLeft
      gridWidth
      gridHeight
      isDragging
      isResizing
      dragEnabled
      resizeEnabled
    } = params

    gridSize = unwrap(gridSize) ? 1
    minWidth = unwrap(minWidth) ? 1
    minHeight = unwrap(minHeight) ? 1
    isDragging or= ->
    isResizing or= ->

    $dom = $(element)
    $dom.css
      top: gridSize * gridTop()
      left: gridSize * gridLeft()
    $dom.width gridSize * gridWidth()
    $dom.height gridSize * gridHeight()
    $dom.draggable
      disabled: not dragEnabled?()
      grid: [gridSize, gridSize]
      start: ->
        isDragging true
      stop: ->
        isDragging false

        {top: domTop, left: domLeft} = $dom.position()

        gTop = Math.max Math.ceil(domTop / gridSize), 0
        gLeft = Math.max Math.ceil(domLeft / gridSize), 0

        $dom.css
          top: gridSize * gTop
          left: gridSize * gLeft

        gridTop(gTop)
        gridLeft(gLeft)

        # Marker for pui_contentEditable not to trigger on the click event
        $dom.data 'pui-was-dragged', true
        setTimeout =>
          $dom.blur()
          if window.getSelection
            window.getSelection().removeAllRanges()
          else if document.selection
            document.selection.empty()
          $dom.data 'pui-was-dragged', false
        , 1 # delay until all events have been processed
    $dom.resizable
      disabled: not resizeEnabled?()
      grid: gridSize

      minWidth: minWidth * gridSize
      minHeight: minHeight * gridSize
      start: ->
        isResizing true
      stop: ->
        isResizing false

        gWidth = Math.max Math.ceil($dom.width() / gridSize), minWidth
        gHeight = Math.max Math.ceil($dom.height() / gridSize), minHeight

        $dom.width gWidth * gridSize
        $dom.height gHeight * gridSize

        gridWidth?(gWidth)
        gridHeight?(gHeight)

    dragEnabled?.subscribe? =>
      $dom.draggable 'option', 'disabled', not dragEnabled()
    resizeEnabled?.subscribe? =>
      $dom.resizable 'option', 'disabled', not resizeEnabled()
}

_registeredBindings = {}
register = (bindings) =>
  _.extend _registeredBindings, bindings

init = ->
  #Initialize polychart-specific bindings.
  _.extend(ko.bindingHandlers, _registeredBindings)

register({
  pui_dndContainer
  pui_contentEditable
  pui_jqDraggableResizeable
  SlickgridData
  DropdownSingle
  DropdownMulti
})

module.exports = {
  init
  register
}


