require('poly/main/init')
ChartMainView                       = require('poly/main/main/chartbuilder')
ChartViewerMainView                 = require('poly/main/main/chartviewer')
DashMainView                        = require('poly/main/main/dashbuilder')
DashViewerMainView                  = require('poly/main/main/dashviewer')
{LocalDataSource, RemoteDataSource} = require('poly/main/data/dataSource')

module.exports = {
  dashboard: (params) ->
    # Mark the target element
    $(params.dom).addClass 'polychart-ui'

    view = new DashMainView(params)
    ko.renderTemplate("tmpl-main", view, {}, params.dom)
    # return only the public facing functions
    serialize: view.serialize

  dashviewer: (params) ->
    # Mark the target element
    $(params.dom).addClass 'polychart-ui'

    view = new DashViewerMainView(params)
    ko.renderTemplate("tmpl-dashboard-viewer", view, {}, params.dom)
    return {} # is there something to be returned?

  chartbuilder: (params) ->
    # Mark the target element
    $(params.dom).addClass 'polychart-ui'

    view = new ChartMainView(params)
    ko.renderTemplate("tmpl-main-chart", view, {}, params.dom)
    # return only the public facing functions
    serialize: view.serialize

  chartviewer: (params) ->
    # Mark the target element
    $(params.dom).addClass 'polychart-ui'

    view = new ChartViewerMainView(params)
    ko.renderTemplate("tmpl-chart-viewer", view, {afterRender: view.init}, params.dom)
    return {} # is there something to be returned?

  data: (args) ->
    switch args.type
      when 'local'
        new LocalDataSource(args.tables)
      when 'remote'
        new RemoteDataSource(args.dataSourceKey, args.customBackend, args.dataSourceType)
}
