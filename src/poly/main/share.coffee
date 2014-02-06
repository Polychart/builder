###
# Hook up events for the share panel.
###
CONST     = require('poly/main/const')
Events    = require('poly/main/events')
serverApi = require('poly/common/serverApi')

class ShareView
  constructor: () ->
    @defaultPanelRight = -250
    @panelRight = ko.observable(@defaultPanelRight)
    Events.nav.sharepanel.open.on @open
    Events.nav.sharepanel.close.on @close

  open: () =>
    @panelRight(0)

  close: () =>
    @panelRight(@defaultPanelRight)

  exportPDF: ->
    Events.export.pdf.click.trigger callback: @_export('pdf')

  exportPNG: ->
    Events.export.png.click.trigger callback: @_export('png')

  exportSVG: ->
    Events.export.svg.click.trigger callback: @_export('svg')

  _export: (type) -> (serial) ->
    serverApi.sendPost(
      "/dashboard/export/code"
    , {serial: serial, exportType: type}
    , (err, result) ->
      if err
        console.error err
        TOAST.raise 'Error exporting dashboard.'
        return

      window.location = "/api/dashboard/export/" + encodeURIComponent(result.code)
    )

module.exports = ShareView
