###
# Define an overlay layer, on which Dropdowns and Dialog boxes may be constructed.
###
Events = require('poly/main/events')
CONST  = require('poly/main/const')

class OverlayView
  constructor: () ->
    @shadeVisible = ko.observable(false)
    #### Dropdown overlays
    @dropdown        = ko.observable(null)
    @dropdownEnabled = true

    Events.ui.dropdown.disable.on @disableDropdown
    Events.ui.dropdown.enable.on @enableDropdown

    Events.ui.dropdown.show.on @handleDropdownShow
    Events.ui.dropdown.hide.on @handleDropdownHide
    Events.ui.highlight.begin.on @beginHighlight
    Events.ui.highlight.end.on @endHighlight

    #### Dialog overlays
    @dialog = ko.observable(null)

    Events.ui.dialog.show.on @showDialog
    Events.ui.dialog.hide.on @hideDialog

  disableDropdown: =>
    @dropdownEnabled = false
    @handleDropdownHide()

  enableDropdown: =>
    @dropdownEnabled = true

  # options: {
  #   templateName: the template to render in the dropdown
  #   data: data to pass to the dropdown template,
  #   targetDom: the target to render the dropdown below
  # }
  handleDropdownShow: (event, options) =>
    # Hide any existing dropdowns
    @handleDropdownHide()

    return unless @dropdownEnabled

    @dropdown(options)
    # Disable scrolling so that it doesn't mess with overlay positions
    $("BODY").addClass("scrolling-disabled")
    $(document).on("click", @handleDocumentClick)

    if options?.targetDom?
      Events.ui.dropdown.shown.triggerElem options.targetDom

  handleDropdownHide: (e) =>
    $(document).off("click", @handleDocumentClick)
    $("BODY").removeClass("scrolling-disabled")

    if @dropdown()?.targetDom?
      Events.ui.dropdown.hidden.triggerElem @dropdown().targetDom
      if not e
        Events.ui.dropdown.hide.trigger()

    @dropdown(null)

  layoutDropdown: (@dropdownDom, dropdown) =>
    $parent = $(@dropdownDom).parents("#dropdown-container")
    $(@dropdownDom).css {
      top:  dropdown.targetDom.offset().top - $parent.offset().top + 40
      left: dropdown.targetDom.offset().left - $parent.offset().left
    }
    $(".cover-top", @dropdownDom).css {
      # Tried innerWidth(), but this yields more pixel-perfect results
      width: dropdown.targetDom.outerWidth() - 2
    }

    # Call custom afterRender as well if necessary
    if dropdown.afterRender
      dropdown.afterRender()

  handleDocumentClick: (event) =>
    return if @dropdown() is null

    # Don't clear overlay if the user just clicked the overlay target
    if (@dropdown().targetDom.get(0) == event.target ||
        @dropdown().targetDom.has(event.target).length > 0)
      return true

    # Don't clear overlay if the user clicked the overlay itself
    found = false
    if (@dropdownDom == event.target ||
        $(@dropdownDom).has(event.target).length > 0)
      found = true

    if !found
      @handleDropdownHide()

  # options: {
  #   selector: a selector string to highlight
  #   click: a handler for when an item in the selector is clicked
  # }
  beginHighlight: (event, options) =>
    @shadeVisible(true)
    $("#shadeOverlay").click (event) =>
      Events.ui.highlight.click.trigger() unless event.isDefaultPrevented()
      @endHighlight()

    return unless options && options.selector
    _.each $(options.selector), (dom) =>
      $dom = $(dom)
      $parent = $(dom).parents(".polychart-ui")

      clone = $dom.clone()
      clone.css
        position: "absolute"
        left: $dom.offset().left - $parent.offset().left
        top: $dom.offset().top - $parent.offset().top
        width: $dom.width()
        height: $dom.height()
      $("#shadeOverlay").append(clone)

      (_.isFunction options.click) && clone.click (event) =>
        options.click(event, $dom)
        event.preventDefault()

  endHighlight: () =>
    @shadeVisible false
    $("#shadeOverlay").html ""
    $('.highlight').removeClass 'highlight'

  #  options: {
  #    template: Template name to bind to
  #    type:     Extra information about type of dialog; currently not used
  #    view:     Model view for the template
  #    shadeVisible: Boolean to set whether or not shade is visible; default is true
  #  }
  showDialog: (event, options={}) =>
    return if not (options.template? and options.view?)
    @shadeVisible(options.shadeVisible ? true)
    @dialog(options)

  hideDialog: () =>
    @dialog(null)
    @shadeVisible(false)

module.exports = OverlayView
