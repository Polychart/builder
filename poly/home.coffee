require('poly/main/init')
Events               = require('poly/main/events')
TOAST                = require('poly/main/error/toast')

DataSourceFormView   = require('poly/dsform')
NuxView              = require('poly/nux')

serverApi            = require('poly/common/serverApi')

NUX_STEPS = [
  {
    cover: 'HEADER, .data-panel',
    title: 'Welcome to Polychart!'
    msgs: [
      "Polychart lets you easily create dashboards and charts from your existing database.",
      "We've created a sample dashboard to help you get started."
    ]
    template: 'tmpl-nux-dash-of-dashes',
    instructions: [
      {text: 'Click the demo dashboard'}
    ],
    skippable: true,
    ref: '.data-panel',
    top: 110,
    left: 15,
    arrowDir: 'right'
  }
]

class HomeView
  constructor: ({availableDataSourceTypes}) ->
    @_availableDataSourceTypes = availableDataSourceTypes

    @deletingDs = ko.observable(false)
    @delDialogTop = ko.observable(0)
    @delDialogLeft = ko.observable(0)

    @newDsView = ko.observable(false)

    @nuxView = null

    dsCount = $(".dash-btns").length
    tutorialCompleted = $('#nux-container').data('tutorialCompleted')
    if dsCount == 0 and not tutorialCompleted
      @showNux()

  showNux: () =>
    if $("#demo").length # only show if demo dashboard exists
      @nuxView = new NuxView({
        steps: NUX_STEPS,
        onSkip: =>
          Events.ui.nux.skip.trigger()
          serverApi.sendPost '/tutorial/mark-complete', {type: 'nux'}, (err) ->
            console.error err if err
      })

  btnKeyPress: (view, event) =>
    if event.which is 13 # enter key
      $(event.target).click()
      return false

    return true

  btnCreateDash: (view, evt) =>
    ds = $(evt.target).parents('.dash-btns')
    key = ds.data('key')
    name = ds.data('name')
    if !key || !name
      throw "Invalid attributes on create-dash button"
    @createDash(key, name)

  btnDeleteDash: (view, evt) =>
    try
      node = evt.target
      while $(node).attr('class') != 'btn-flat delete-dash'
        node = node.parentNode
    catch e
      throw "Invalid click target"
    key = $(node).attr("data-key")
    if !key
      throw "Invalid attributes on delete-dash button"
    @deleteDash(key)

  showDeleteDsDialog: (view, evt) =>
    dsKey = $(evt.target).closest('.dash-btns').data('key')
    @deletingDs(dsKey)
    @delDialogTop($(evt.target).offset().top)
    @delDialogLeft($(evt.target).offset().left)

  hideDeleteDsDialog: () =>
    @deletingDs(false)

  btnConfirmDeleteDs: (view, evt) =>
    Events.ui.datasource.remove.trigger()
    dsKey = @deletingDs()
    serverApi.sendPost '/data-source/' + dsKey + '/delete', {}, (err) ->
      if err
        console.error err
        TOAST.raise 'Error deleting data source'
      else
        window.location = '/home'

  dashboardMouseEnter: (view, evt) =>
    $dom = $(evt.target).closest(".dashboard-preview")
    $(".dashboard-info", $dom).css
      height: $dom.height()
      bottom: $dom.height()
    $(".dashboard-options", $dom).stop(true, true).fadeIn()
    $(".dashboard-title", $dom).stop(true, true).fadeOut("fast")

  dashboardMouseLeave: (view, evt) =>
    $dom = $(evt.target).closest(".dashboard-preview")
    $(".dashboard-info", $dom).css
      height: "35px"
      bottom: "35px"
    $(".dashboard-options", $dom).stop(true, true).fadeOut()
    $(".dashboard-title", $dom).stop(true, true).fadeIn()

  createDash: (dsKey, name) =>
    callback = (err, response) ->
      if err
        console.error err
        TOAST.raise 'Error creating dashboard'
      else
        dom = $("#dashboard-item-template").clone()
        dom.removeClass "template"
        $(".dashboard-name", dom).html name
        $(".dashboard-name", dom).attr "href", "dashboard/" + response.key + "/edit"
        $(".dashboards").append dom
        window.location = "/home?newDashboardKey=#{encodeURIComponent(response.key)}"

    data =
      name: name
      spec: {}
      dataCollection: [
        dataSourceKey: dsKey
        tableNames: ['nothing']
      ]
    serverApi.sendPost '/dashboard/create', data, callback

  deleteDash: (dsKey) =>
    serverApi.sendPost '/dashboard/' + dsKey + '/delete', {}, (err, response) ->
      if err
        console.error err
        TOAST.raise 'Error deleting dashboard'
      else
        window.location = '/home'

  toggleDataSourceForm: (view, evt) =>
    if !$('#new-data-source').is(":visible")
      Events.nav.dscreate.start.trigger()
      @newDsView(new DataSourceFormView(@_availableDataSourceTypes))
      $('#dashboard-shade').fadeIn('fast')
      $(evt.target).closest('.btn-large').addClass('active')
    else
      @newDsView(false)
      $('#dashboard-shade').fadeOut()
      $('.btn-large').removeClass('active')

  btnLogout: () =>
    window.location = '/logout'

module.exports.main = (params) =>
  homeView = new HomeView(params)
  ko.applyBindings homeView
