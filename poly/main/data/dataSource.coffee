Events    = require('poly/main/events')
TOAST     = require('poly/main/error/toast')
serverApi = require('poly/common/serverApi')

# A source of zero or more data tables
class DataSource
  dsType: 'abstract'

  constructor: ->
    throw new Error('DataSource is abstract')

  listTables: (callback) ->
    throw new Error('DataSource is abstract')

  createPolyJsData: (meta) ->
    throw new Error('DataSource is abstract')

  getRange: (column, callback) ->
    throw new Error('DataSource is abstract')

# Entire data set provided to constructor
class LocalDataSource extends DataSource
  dsType: 'local'

  constructor: (tables) ->
    @_localData = tables

    @_tableList = {}
    for table in tables
      # TODO: Remove this terrible hack for local data and name format of
      #       "tableName.columnName"---need this to get js to work properly with that.
      if _.isArray(table.data)
        jsData = []
        for item in table.data
          newItem = {}
          for columnName, column of item
            newItem["#{table.name}.#{columnName}"] = column
          jsData.push newItem
      else if _.isObject(table.data)
        jsData = {}
        for columnName, column of table.data
          jsData["#{table.name}.#{columnName}"] = column

      jsMeta = {}
      for columnName, meta of table.meta
        jsMeta["#{table.name}.#{columnName}"] = meta
      @_tableList[table.name] =
        name: table.name
        meta: table.meta
        jsdata: polyjs.data {data: jsData, meta: jsMeta}
        rawdata: polyjs.data table

  listTables: (callback) =>
    callback null, @_tableList

  createPolyJsData: (meta) =>
    {tableName} = meta

    # If meta is a hash of aesthetics' metadata rather than a singe metadata object
    # Because we're about as consistent with meta as we are with spec
    for aes, submeta of meta when tableName is null
      {tableName} = submeta

    @_tableList[tableName].rawdata

  getRange: ({tableName, name, derived, fullFormula, type}, callback=->) ->
    {jsdata} = @_tableList[tableName]

    if type == 'cat'
      base = polyjs.parser.getExpression(fullFormula).expr
      meta = {}
      meta["#{polyjs.parser.unbracket fullFormula}"] = type: type
      dataspec =
        select: [base]
        stats:
          stats: []
          groups: []
        trans: if derived then [base] else []
        filter: []
        limit: 100
        meta: meta
    else
      base = polyjs.parser.getExpression(fullFormula).expr
      min = polyjs.parser.getExpression("min(#{fullFormula})").expr
      max = polyjs.parser.getExpression("max(#{fullFormula})").expr
      meta = {}
      meta["min(#{fullFormula})"] = type: type
      meta["max(#{fullFormula})"] = type: type
      dataspec =
        select: [min, max]
        stats:
          stats: [{
            name: "min"
            expr: min
            args: [base]
          },{
            name: "max"
            expr: max
            args: [base]
          }]
          groups: []
        trans: if derived then [base] else []
        filter: []
        limit: 2
        meta: meta

    wrappedCallback = (err, jsdata) =>
      if err?
        TOAST.raise(err.message)
        callback(err)
        return
      if type == 'cat'
        formula = polyjs.parser.unbracket fullFormula
        callback null, values: _.uniq _.pluck(jsdata.raw, formula)
      else
        # because the column name may be normalized to something other than
        # "min(#{fullFormula})", we take the safer route of assuming that
        # the min value always comes first
        values = _.toArray(jsdata.raw[0])
        callback null,
          min: values[0]
          max: values[1]
    jsdata.getData wrappedCallback, dataspec


DEFAULT_BACKEND = (request, callback) ->
  path = "/data-source/#{encodeURIComponent(request.dataSourceKey)}"

  if request.command is 'listTables'
    path += '/tables/list'
    params = {}
  else if request.command is 'getColumnMetadata'
    path += '/tables/meta'
    params = {
      tableName: request.tableName
      columnExpr: request.columnExpr
      type: request.dataType
    }
  else if request.command is 'queryTable'
    path += '/tables/query'
    params = {
      spec: JSON.stringify request.query
    }
  serverApi.sendQueryPost path, params, callback

class RemoteDataSource extends DataSource
  constructor: (@dataSourceKey, @backend=DEFAULT_BACKEND, @dsType) ->

  listTables: (callback) ->
    @backend {
      command: 'listTables'
      @dataSourceKey
    }, (err, tables) =>
      if err
        callback err, null
        return

      result = {}
      for table in tables
        result[table.name] = table
        result[table.name].jsdata = @createPolyJsData(table.name)
        for col of result[table.name].meta
          result[table.name].meta[col].dsKey = @dataSourceKey
      if _.values(_.values(result)[0].meta)[0].ga? then Events.ui.ga.notify.trigger()
      callback null, result

  createPolyJsData: (meta) ->
    {tableName} = meta
    # If meta is a hash of aesthetics' metadata rather than a singe metadata object
    for aes, submeta of meta
      break if tableName?
      {tableName} = submeta

    cache = {}
    polyjs.data.api (requestParams, callback) =>
      for key, val of requestParams.meta # Compatibility with old code
        unless key is '_additionalInfo'
          if tableName and not val.tableName then val.tableName = tableName
          if 'dsKey' not of val then val.dsKey = @dataSourceKey
        requestParams.meta[key] = _.extend requestParams.meta[key], val

      paramJson = JSON.stringify(requestParams)

      if paramJson of cache and _.size(cache[paramJson].data) > 0
        callback null, cache[paramJson]
      else
        @backend {
          command: 'queryTable'
          @dataSourceKey
          query: requestParams
        }, (err, res) ->
          if err then callback err, null
          else
            if res?.data?.length
              cache[paramJson] = res
              callback null, res
            else
              callback {message: "No data matching criteria"}, res
          return null

  # getRange
  #   Function to get the range of data; mainly to obtain meta information
  #   relevant for Filters. Parameters:
  #
  #   dsInfo : Object
  #     ~ Object to specify location of information with fields:
  #     { dsKey      : String
  #     { tableName  : String
  #     { derived    : Boolean
  #     { fullFormula: String
  #     { type       : String
  #   callback       : Function
  #     ~ Function that is passed (Error, Result), where
  #     { Error      : JSON  # TODO: Specify error format
  #     { Result     : JSON
  #       if type == 'cat' then { values : [String]
  #       else                  { max    : Num or Date
  #                             { min    : Num or Date
  getRange: ({tableName, name, derived, fullFormula, type}, callback) ->
    @backend {
      command: 'getColumnMetadata'
      @dataSourceKey
      tableName: tableName
      columnExpr: JSON.stringify polyjs.parser.getExpression(fullFormula).expr
      dataType: type
    }, (err, meta) ->
      if err
        callback err, null
        return

      callback null, meta

module.exports = {LocalDataSource, RemoteDataSource}
