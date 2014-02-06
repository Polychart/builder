#### Event tree and instantiation for the dashboard builder.
EventsFactory = require('poly/common/events')

dbbEventTree =
  signup:
    page:
      view:
        tracked:        true
        noninteraction: true
    form:
      interact:
        tracked: true
      submit:
        tracked: true
      error:
        tracked: true
    eula:
      error:
        tracked: true
  ui:
    dropdown:
      show: {}
      shown: {}
      hide: {}
      hidden: {}
      choose: {}
      disable: {}
      enable: {}
    numeral:
      add: {}
      render: {}
      edit: {}
    pivottable:
      add: {}
      render: {}
      edit: {}
    chart:
      render: {}
      add: {}
      edit: {}
    dashboarditem:
      remove: {}
      select: {}
    quickadd:
      add:    {}
      click: {}
      expand: {}
      collapse: {}
    layer:
      remove: {}
    metric:
      add: {}
      remove: {}
    filter:
      remove: {}
    highlight:
      begin: {}
      end: {}
      click: {}
    backtodbb:
      click: {}
    title:
      add: {}
    dnd:
      start: {}
      drop: {}
      reject: {}
      selectdroppable: {} # when the user clicks a drop target
      selectdraggable: {} # when the user chooses a metric to place in the drop target
    table:
      focus: {} # when chart editor opens, signal which table is opened
      open: {}
    nux:
      skip:
        tracked: true
      firstdb:
        tracked: true
      datapanel:
        tracked: true
      datatable:
        tracked: true
      chartspanel:
        tracked: true
      workspace:
        tracked: true
      layerspanel:
        tracked: true
      layerspanel2:
        tracked: true
      layerspanel3:
        tracked: true
      tablepanel:
        tracked: true
      workspace2:
        tracked: true
      tableedit:
        tracked: true
      tableedit2:
        tracked: true
      workspace3:
        tracked: true
      datapanel2:
        tracked: true
      datanewcol:
        tracked: true
      workspace4:
        tracked: true
      numeral:
        tracked: true
      done:
        tracked: true
    ga:
      notify:
        tracked: false
      done:
        tracked: false
    datasource:
      remove:
        tracked: true
    dialog:
      show: {}
      hide: {}
  nav:
    home:
      open:
        tracked: true
    chartbuilder:
      open:
        tracked: true
    numeralbuilder:
      open:
        tracked: true
    tablebuilder:
      open:
        tracked: true
    datatableviewer:
      open:
        tracked: true
      close:
        tracked: true
    dashbuilder:
      open:
        tracked: true
    dashviewer:
      open:
        tracked: true
    sharepanel:
      open:
        tracked: true
      close:
        tracked: true
    dscreate:
      nextstep: {}
      start:
        tracked: true
      connscript:
        tracked: true
      dbtype:
        tracked: ['details']
      conntype:
        tracked: ['details']
      ssh:
        tracked: true
      socket:
        tracked: true
      direct:
        tracked: true
      dbacc:
        tracked: true
      csvchoose:
        tracked: true
      csvcancel:
        tracked: true
      csvfail:
        tracked: ['details']
      csvcomplete:
        tracked: true
      name:
        tracked: true
      oautherr:
        tracked: ['details']
      error:
        tracked: ['details']
      success:
        tracked: true
  model:
    dashboarditem:
      create: {}
      update: {}
      delete: {}
  error:
    polyjs:
      data:
        tracked: true
  share:
    email:
      click:
        tracked: true
    copyurl:
      click:
        tracked: true
    copyimage:
      click:
        tracked: true
  export:
    pdf:
      click:
        tracked: true
    png:
      click:
        tracked: true
    svg:
      click:
        tracked: true
  data:
    column:
      update: {}
      delete: {}
      add: {} # NUX
      new: {}

defaultPropHandler = (name, defaults) ->
  if name is 'tracked' and defaults?
    tracked = tracked
    unless _.isArray tracked
      tracked = []

    _listener = (evt, info) ->
      if not _.isObject(info) and info?
        info = info: "#{info}"
      target = _.extend {}, tracked, info
      result = {}
      for key in _.union(['server', 'cid'], tracked)
        result[key] = target[key]
      EventsFactory._track "dbb_#{name}", result

    @_defaultListeners[name] = _.throttle(_listener, 10, true)

Events = EventsFactory.getTree dbbEventTree, defaultPropHandler
Events.registerDefaultListeners = EventsFactory._registerDefaultListeners

module.exports = Events
