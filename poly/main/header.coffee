###
# Register events and functions for buttons in the header. Along with that, set
# up some global event triggers such as tutorial buttons, showing the share
# panel and back buttons.
###
Events = require('poly/main/events')
CONST  = require('poly/main/const')

class HeaderView
  #### View model underlying the header; provides UI functions for buttons
  constructor: (@isDemo) ->
    @sharePanelVisible        = false
    @dashboardControlsVisible = ko.observable(true)

    # Events to close share panel when opening other environments
    for items in ['numeral', 'pivottable', 'chart']
      Events.ui[items].edit.on () =>
        if @sharePanelVisible then @toggleSharePanel()
    for items in ['chartbuilder', 'numeralbuilder', 'tablebuilder']
      Events.nav[items].open.on () =>
        if @sharePanelVisible then @toggleSharePanel()

    Events.ui.backtodbb.click.on (event, params) =>
      Events.nav.dashbuilder.open.trigger(params)

    unless isDemo
      Events.nav.chartbuilder.open.on () =>
        @dashboardControlsVisible(false)
      Events.nav.dashbuilder.open.on () =>
        @dashboardControlsVisible(true)

  backToHome: (event) =>
    #### UI function to open the Home view
    Events.nav.home.open.trigger()
    return false

  toggleSharePanel: (self, e) =>
    #### UI function to open the share panel
    @sharePanelVisible = !@sharePanelVisible
    if @sharePanelVisible
      Events.nav.sharepanel.open.trigger()
      $("#export-btn").addClass('active')
    else
      Events.nav.sharepanel.close.trigger()
      $("#export-btn").removeClass('active')
    return

module.exports = HeaderView
