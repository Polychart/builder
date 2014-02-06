#### Module that defines representations for joins and UI elements to edit them.
#
# The following are the main things defined in this module.
#
#   JoinsView           - A model for Joins at the Layer level
#   JoinsEditorBasic    - A UI model for the basic joins editor.
#   JoinsEditorAdvanced - A UI model for the advaned joins editor.
#
Events = require('poly/main/events')

TOAST  = require('poly/main/error/toast')

class JoinsView
  #### A class representing joins between tables in a layer
  #
  # This class contains the data and methods to manipulate joins between tables
  # with respect to the metrics attached to a layer.
  #
  # Attributes:
  #   tableMetaData: Object
  #     This is an object from which metadata about tables in the data source
  #     may be obtained. See `data/dataView.coffee` for more information.
  #
  #   editor: Object
  #     The layover joins editor screen view.
  #
  #   parent: Object
  #     Parent object that contains this. Must have an `attachedMetrics()`
  #     observable listing all observed metrics.
  #     Could be instances of class
  #       * LayerView
  #       * QuickAddItemView
  #
  #   tables: ko.observable(JSON object)
  #     This is an observable containing key-value pairs, whose keys are table
  #     names corresponding to tables which are involved in some join, and values
  #     of table objects, as defined below.
  #
  #   renderable: ko.observable(Boolean)
  #     A wrapped flag that denotes whether or not the current joins allows for
  #     a successful query. False when joins are being edited.
  #
  #   joins: ko.computed([Joins])
  #     A wrapped array that contains the unique joins present in the model.
  #
  constructor: (@tableMetaData, spec={}, @parent) ->
    @viewer        = new JoinsViewer(@tableMetaData)
    @editor        = new JoinsEditorView(@tableMetaData)
    @tables        = ko.observable({})
    @renderable    = ko.observable(false)
    @hasJoins      = ko.computed () => _.size(@tables()) >= 2
    @joins         = ko.computed () =>
      tables   = @tables()
      allJoins = _.flatten(_.values(table.joins) for name_, table of tables)
      _.filter allJoins, (join, i) =>
        _.every allJoins.slice(i+1), (item) => not join.equal(item)
    @initialize(spec)
    @renderable(true)

  reset: (spec={}) ->
    @tables({})
    @initialize(spec)

  openViewer: () => @viewer.open(@joins)

  initialize: (spec) =>
    #### Initialize the view with initial specification
    #
    # Args:
    #   spec: JSON object
    #     This is an object that contains information on what tables are present
    #     and what joins are present amongst the tables. It shall have the
    #     following form
    #
    #       spec = { tables: ["tableOne", "tableTwo", ...]
    #                joins: [ { type: "inner"
    #                           table1: "tableOne"
    #                           table2: "tableTwo"
    #                           column1: "columnName1"
    #                           column2: "columnName2" }, ...] }
    #
    if not _.isEmpty(spec)
      tables = @tables()
      for name in (spec.tables ? [])
        tables[name] = new Table(name)
      for join in (spec.joins ? [])
        {table1, table2, column1, column2} = join
        new Join(tables[table1], column1, tables[table2], column2)
      @tables(tables)
      return
    # We don't have a spec, but let's check if something fishy is going on
    if @parent.attachedMetrics?
      tableNames = _.uniq (m.tableName for m in @parent.attachedMetrics())
      if _.size(tableNames) >= 2
        @renderable(false)
        TOAST.raise("Information about table joins is missing! Cannot render.")
        return
      # Still have to check whether there is a single table
      if _.size(tableNames) == 1
        tables = @tables()
        name = tableNames[0]
        tables[name] = new Table(name)
        @tables(tables)

  checkAddJoins: (event, item, callback) =>
    {tableName} = item.data
    tables = @tables()
    if _.isEmpty(tables) or tableName of tables # no new joins
      if _.isEmpty(tables)
        tables[tableName] = new Table(tableName)
      @tables(tables)
      callback()
      return

    # google analytics data - joins are handled by server
    if @tableMetaData.dsType is 'googleAnalytics'
      callback()
      return
    # need to get a new join, but non-remote data source
    if @tableMetaData.dsType not in ['mysql', 'postgresql', 'infobright']
      TOAST.raise "You cannot use two different data tables/sources."
      return

    # actually get a new join...
    @renderable(false) # prevent render
    if not (tableName of tables)
      @editor.open(tables, tableName, @wrappedCallback(callback))

  wrappedCallback: (realCallback) => (success, newJoinParams) =>
    @renderable(true) # allow render
    if not success
      TOAST.raise("Oops. Adding that column failed.")
      return
    @editorAddJoin(newJoinParams)
    realCallback()
    
  editorAddJoin: (params) =>
    #### Method callable from a Joins Editor view to add a join
    #
    # Args:
    #   params: Object
    #     This is a JSON-object that looks as follows
    #
    #       params = { table1: "table1Name"
    #                  table2: "table2Name"
    #                  column1: "firstColumnName"
    #                  column2: "secondColumnName" }
    #
    #     This is deconstructed and passed as the arguments to the Join object
    #     constructor.
    #
    # Returns: Maybe String
    #   The function is called primarily for the effect of updating the @tables
    #   object stored in the model, along with the join-relations between
    #   tables therein. However, this function also returns the result of
    #   `@checkJoins`, which is a `Maybe String` denoting any tables that still
    #   need to be joined.
    #
    {table1, table2, column1, column2} = params
    tables          = @tables()
    tables[table2]  = new Table(table2) # table2 is always the new table
    new Join( tables[table1], column1
            , tables[table2], column2 )
    @tables(tables)

  checkRemoveJoins: () =>
    # google analytics data - joins are handled by server
    if @tableMetaData.dsType is 'googleAnalytics'
      return
    tableNames = _.uniq (m.tableName for m in @parent.attachedMetrics())
    tables = @tables()
    unattachedTables = _.difference _.keys(tables), tableNames
    for table in unattachedTables
      if tables[table].canDelete()
        tables[table].delete()
        delete tables[table]
    @tables(tables)

  generateSpec: () =>
    #### Generates a JSON object specifying the view
    #
    # Args:
    #   No arguments are explicitly passed in, though the `@tables` parameter
    #   is assumed to exist within the object as a `ko.observable(JSON)`.
    #
    # Returns:
    #   A JSON object is returned in the form
    #
    #   spec = { tables: ["tableOne", "tableTwo", ...]
    #            joins: [ { type: "inner"
    #                       table1: "tableName1"
    #                       table2: "tableName2"
    #                       column1: "columnName1"
    #                       column2: "columnName2" }, ...] }
    #
    joinObjs = _.unique(_.flatten(_.values(t.joins) for name, t of @tables()))
    tables: _.keys(@tables())
    joins: (j.generateSpec() for j in joinObjs)

class JoinsViewer
  template:    'tmpl-joins-viewer'
  constructor: (@tableMetaData) ->
  open: (@joins) ->
    Events.ui.dialog.show.trigger
      template: @template
      type:     'joins-viewer'
      view:     @
  close: (elem) =>
    Events.ui.dialog.hide.trigger()

class JoinsEditorView
  template:    'tmpl-joins-editor-basic'
  constructor: (@tableMetaData) ->
  open: (@tables, @newTable, @callback) ->
    _pair = (obj) -> [obj, obj]
    # Set up selector data for the UI
    @newTableDummy    = [newTable]
    @newTableSelDummy = ko.observable _pair newTable
    @newVars          = @tableMetaData.getColumnsInTable @newTable
    @newVarSel        = ko.observable(_pair @newVars[0])
    @existingTables = _.without(_.keys(@tables), @newTable)
    @existingTableSel = ko.observable(_pair @existingTables[0])
    @existingVars     = ko.computed () =>
      @tableMetaData.getColumnsInTable @existingTableSel()[0]
    @existingVarSel   = ko.observable(_pair @existingVars()[0])
    @existingVars.subscribe (val) =>
      if @existingVarSel()[0] not in val
        @existingVarSel(_pair @existingVars()[0])
    @joinTypes   = [['Inner Join', 'inner']]
    @joinTypeSel = ko.observable @joinTypes[0]
    Events.ui.dialog.show.trigger
      template: @template
      type:     'joins-editor-basic'
      view:     @

  cancelJoin: () =>
    @close()
    @callback false

  confirmJoin: () =>
    #### UI function to pass new joins data to model
    # The function is called by the `Confirm Joins` button in the add joins UI.
    @close()
    @callback true, {
        type: 'inner'
      , table1: @existingTableSel()[1]
      , table2: @newTable
      , column1: @existingVarSel()[1]
      , column2: @newVarSel()[1]
    }

  close: () => Events.ui.dialog.hide.trigger()

#### Classes to help represent joins

class Table
  #### Model to hold information about tables; serves as a vertex in joins graph
  constructor: (@name) ->
    @joins = {}
  canDelete: () =>
    # here, we assume that there are no cycles in the graph
    # if the number of edges (joins) connected to this node (table)
    # is 1, then this node is safe to remove
    _.size(@joins) <= 1
  delete: () => join.remove() for key, join of @joins
  addJoin: (withTable, join) => @joins[withTable] = join
  removeJoin: (withTable) => delete @joins[withTable]

class Join
  #### Model for information about joins; serves as an edge in joins graph
  constructor: (@table1, @column1, @table2, @column2) ->
    @table1.addJoin(@table2.name, @)
    @table2.addJoin(@table1.name, @)
    @type = 'inner'
  remove: () =>
    @table1.removeJoin(@table2.name)
    @table2.removeJoin(@table1.name)
  generateSpec: () =>
    type:    @type
    table1:  @table1.name
    table2:  @table2.name
    column1: @column1
    column2: @column2
  equal: (other) =>
    #### A helper to determine whether two joins are equal
    #
    # Two joins are considered equal if they either are the same in each field,
    # or their tables and columns differ only in order.
    #
    specOne = @generateSpec()
    specTwo = other.generateSpec()
    if _.isEqual specOne,specTwo
      true
    else
      _.every([ specOne.type    is specTwo.type
                specOne.column1 is specTwo.column2
                specOne.column2 is specTwo.column1
                specOne.table1  is specTwo.table2
                specOne.table2  is specTwo.table1 ])

module.exports = {JoinsView}
