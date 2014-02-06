Events     = require('poly/main/events')
PolyJSItem = require('poly/main/dash/item/polyjs')

CONST      = require('poly/main/const')
TOAST      = require('poly/main/error/toast')

class PivotTableItem extends PolyJSItem
  minWidth: 6
  minHeight: 4
  templateName: 'tmpl-pivottable-item'
  constructor: (@spec=null, position={}) ->
    position.width or= 16
    position.height or= 10
    super(@spec, position)

  _initSpec: () =>
    if not @spec.data and @spec.tableName
      tableName = @spec.tableName
      for prop, val of @spec.meta
        if tableName? then break
        if _.isObject(val) and 'var' of val and 'tableName' of val
          tableName = val.tableName
      @spec.data = @tableMetaData.polyJsObjectFor {tableName}
    # generate full meta for backwards compatibility
    for name, value of @spec.meta
      try
        newname =
          if name is 'count(*)'
            'count(1)'
          else
            polyjs.parser.unbracket(polyjs.parser.parse(name).pretty())
        if not @spec.meta[newname] and @spec.meta[name]
          @spec.meta[newname] = @spec.meta[name]
      catch
        #nothing

  _renderPolyJSItem: (spec, loaded, callback) =>
    spec = $.extend(true, {}, spec)
    spec.title ?= spec.tableName
    polyjs.pivot spec, loaded, callback

  serialize: (s={}) ->
    spec = $.extend(true, s, @spec)
    delete spec.dom
    delete spec.data
    super
      itemType: 'PivotTableItem'
      spec: spec

  editPivot: () =>
    Events.ui.pivottable.edit.trigger()
    Events.nav.tablebuilder.open.trigger {
      spec: @spec
      tableView: @
    }

module.exports = PivotTableItem
