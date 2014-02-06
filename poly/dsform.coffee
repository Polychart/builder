Animation = require('poly/main/anim')

TOAST     = require('poly/main/error/toast')

serverApi = require('poly/common/serverApi')
dsEvents  = require('poly/main/events').nav.dscreate

NUM_STEPS = 5

###
This class implements the new data source form. It uses instances of `FormStep`
subclasses, which define their own templates for rendering. They also implement
functions to validate data, extend a data object, and provide the next step
object.

There is also an `allSteps` array, which keeps track of the step objects that
the user has previously visited. This allows the user to step back to make a
correction, without losing information that has been filled out in the following
steps.
###
class DataSourceFormView
  constructor: (availableDataSourceTypes) ->
    @data = {}

    @formStep = ko.observable(new FormStepSourceType(availableDataSourceTypes))
    @stepNum = ko.observable(0)
    @progPercWidth = ko.computed =>
      fullWidth = $('.progress-bar', @dom).width()
      return fullWidth if @formStep() == null
      expectedNumSteps = @formStep().expectedStepsLeft + @stepNum()
      (@stepNum() / expectedNumSteps) * fullWidth

    @allSteps = [@formStep()]
    @actionsDisabled = ko.observable(false)

    @backBtnVisible = ko.computed =>
      formStep = @formStep()
      @stepNum() != 0 and not _.isEmpty formStep.backBtnText
    @nextBtnVisible = ko.computed =>
      @formStep().expectedStepsLeft != 0 and not _.isEmpty @formStep().nextBtnText

    dsEvents.nextstep.on @nextStep

  initFormStep: (dom) =>
    @formStep().initDOM(dom, @data)

  nextStep: () =>
    if @actionsDisabled()
      return false

    if errorMsg = @formStep().getFormErrorMessage(@data)
      TOAST.raise errorMsg
      return false

    loadingAnim = new Animation('loading', @dom)
    @actionsDisabled(true)

    asyncValidateCallback = (resp) =>
      loadingAnim.remove()
      @actionsDisabled(false)

      if _.isString(resp)
        TOAST.raise resp
      else if resp == true
        @formStep().extendFormData(@data)
        nextStep = @formStep().constructNextStep()

        # This makes sure data isn't lost if the user navigates backwards and forwards through the form steps
        if @allSteps.length > @stepNum() + 1
          nextAllStep = @allSteps[@stepNum() + 1]
          if nextAllStep.templateName == nextStep.templateName
            nextStep = nextAllStep
            nextStep.returnToStep()
          else @allSteps = @allSteps.splice(0, @stepNum() + 1)
        else @allSteps.push(nextStep)

        @formStep(nextStep)

        @stepNum(@stepNum() + 1)

    @formStep().asyncFormValidate(asyncValidateCallback, @data)

  prevStep: () =>
    if @actionsDisabled()
      return false

    @formStep().prevStep()
    @formStep(@allSteps[@stepNum() - 1])
    @stepNum(@stepNum() - 1)

  formSubmit: ->
    @nextStep()
    false

  initDataSourceView: (@dom) =>


class FormStep
  constructor: () ->
    @expectedStepsLeft = 6

  # Called when the user clicks the 'back' button
  prevStep: ->

  # When the user returns after clicking back, then forward again
  returnToStep: ->

  backBtnText: 'Back'
  nextBtnText: 'Next Step'

  # May optionally be subclassed, does nothing here
  initDOM: (@dom, data) =>

  # Extend the passed data object with relevant form data
  extendFormData: (data) =>
    throw 'FormStep subclass must implement this method'

  # Return an error message string if invalid form input, else return null
  getFormErrorMessage: (data) =>

  # Implement any async calls here, call the callback when ready
  # Pass the callback an error message if necessary, false if validation failed, and true otherwise
  asyncFormValidate: (callback, data) =>
    callback(true)

  # Return the next FormStep
  constructNextStep: () =>
    throw 'FormStep subclass must construct next step!'


class FormStepSourceType extends FormStep
  constructor: (availableTypes) ->
    @stepName = 'Select Data Source Type'
    @templateName = 'tmpl-nds-form-source-type'
    @expectedStepsLeft = 6
    @type = ko.observable(null)

    allTypeButtons = [
      {name: 'mysql'},
      {name: 'postgresql', wide: true},
      {name: 'salesforce'},
      {name: 'infobright'},
      {name: 'googleAnalytics', wide: true},
      {name: 'csv'},
    ]
    @typeButtons = (b for b in allTypeButtons when b.name in availableTypes)

  typeButtonClicked: (typeButton) =>
    @type typeButton.name

  getFormErrorMessage: =>
    if _.isEmpty @type()
      return "You need to select a data source type!"

  extendFormData: (data) =>
    data.type = @type()

    if @type() == 'postgresql'
      data.connectionType = 'direct'

  constructNextStep: () =>
    dsEvents.dbtype.trigger details: @type()
    switch @type()
      when 'mysql', 'infobright'
        return new FormStepConnectionType()
      when 'postgresql'
        return new FormStepDirectConnection()
      when 'googleAnalytics'
        return new FormStepGAProfileId()
      when 'salesforce'
        return new FormStepDataSourceName()
      when 'csv'
        return new FormStepCsvChoose()


class FormStepConnectionType extends FormStep
  constructor: () ->
    @stepName = 'Select Connection Type'
    @templateName = 'tmpl-nds-form-connection-type'
    @expectedStepsLeft = 5
    @options = ko.observableArray(['ssh', 'direct'])
    @optionsText = (item) =>
      switch item
        when 'ssh' then 'SSH'
        when 'direct' then 'Direct Connection'
    @type = ko.observable()

  extendFormData: (data) =>
    data.connectionType = @type()

  getFormErrorMessage: =>
    if @type() != 'direct' && @type() != 'ssh'
      return "Invalid connection type entered!"

  asyncFormValidate: (callback, data) =>
    if @type() == 'ssh' && (!data.sshKey || !data.sshPublicKey)
      serverApi.sendPost '/ssh/keygen', {}, (err, resp) ->
        if err
          callback('An error occurred contacting the server')
        else
          data.sshKey = resp.privateKey
          data.sshPublicKey = resp.publicKey
          callback(true)
    else
      callback(true)

  constructNextStep: () =>
    dsEvents.conntype.chain dsEvents.dbtype, details: @type()
    if @type() == 'ssh'
      return new FormStepSSH()
    else if @type() == 'direct'
      return new FormStepDirectConnection()


class FormStepSSH extends FormStep
  constructor: () ->
    @stepName = 'Set Up an SSH Account'
    @templateName = 'tmpl-nds-form-ssh'
    @expectedStepsLeft = 4

    @sshUsername = ko.observable('')
    @sshHost = ko.observable('')
    @sshPort = ko.observable('22')
    @sshPublicKey = ko.observable('')

    @requireSocketFilename = false

  initDOM: (dom, data) =>
    if data.type == 'mysql'
      @defaultSocketFile = '/var/run/mysqld/mysqld.sock'
    else if data.type == 'infobright'
      @defaultSocketFile = '/tmp/mysql-ib.sock'

    @sshPublicKey(data.sshPublicKey)

  getFormErrorMessage: =>
    if _.isEmpty @sshUsername()
      return "You must enter an SSH username!"
    if _.isEmpty @sshHost()
      return "You must enter an SSH host!"
    if _.isEmpty @sshPort()
      return "You must enter an SSH port!"

  asyncFormValidate: (callback, data) =>
    data =
      username: @sshUsername()
      host: @sshHost()
      port: @sshPort()
      privateKey: data.sshKey
      filePath: @defaultSocketFile
      isSocket: true

    serverApi.sendPost '/ssh/file-exists', data,
      (err, resp) =>
        if err
          console.error err
          callback('An error occurred contacting the server')
          return

        switch resp.status
          when 'found'
            callback(true)
          when 'notFound'
            @requireSocketFilename = true
            callback(true)
          when 'connFailed'
            callback('SSH authorization failed, please enter the correct credentials.')

  extendFormData: (data) =>
    data.sshUsername = @sshUsername()
    data.sshHost = @sshHost()
    data.sshPort = @sshPort()

    unless @requireSocketFilename
      data.dbUnixSocket = @defaultSocketFile

  constructNextStep: () =>
    dsEvents.ssh.chain dsEvents.dbtype
    if @requireSocketFilename
      return new FormStepSocketFilename()
    else
      return new FormStepDatabaseAccount()


class FormStepSocketFilename extends FormStep
  constructor: () ->
    @stepName = 'Enter Your Unix Socket File'
    @expectedStepsLeft = 3
    @templateName = 'tmpl-nds-form-socket-filename'
    @dbUnixSocket = ko.observable('')

  getFormErrorMessage: =>
    if _.isEmpty @dbUnixSocket()
      return "You must enter a Unix socket file location!"

  extendFormData: (data) =>
    data.dbUnixSocket = @dbUnixSocket()

  asyncFormValidate: (callback, data) =>
    data =
      username: data.sshUsername
      host: data.sshHost
      port: data.sshPort
      privateKey: data.sshKey
      filePath: @dbUnixSocket()
      isSocket: true

    serverApi.sendPost '/ssh/file-exists', data,
      (err, resp) =>
        if err
          console.error err
          callback('An error occurred contacting the server')
          return

        switch resp.status
          when 'found' then callback(true)
          when 'notFound'
            callback('Could not find the UNIX socket file, please enter it again.')
          when 'connFailed'
            callback('SSH authorization failed, please enter the correct credentials.')

  constructNextStep: () =>
    dsEvents.socket.chain dsEvents.dbtype
    return new FormStepDatabaseAccount()

class FormStepDirectConnection extends FormStep
  constructor: () ->
    @stepName = 'Enter the Location of Your Database'
    @templateName = 'tmpl-nds-form-direct-connection'
    @expectedStepsLeft = 3

    @dbHost = ko.observable('')
    @dbPort = ko.observable('')

  initDOM: (dom, data) =>
    return unless _.isEmpty @dbPort()
    switch data.type
      when 'mysql' then @dbPort('3306')
      when 'infobright' then @dbPort('5029')
      when 'postgresql' then @dbPort('5432')

  getFormErrorMessage: =>
    if _.isEmpty @dbHost()
      return "You must enter a database host!"
    if _.isEmpty @dbPort()
      return "You must enter a database port!"

  extendFormData: (data) =>
    data.dbHost = @dbHost()
    data.dbPort = @dbPort()

  constructNextStep: () =>
    dsEvents.direct.chain dsEvents.dbtype
    return new FormStepDatabaseAccount()


class FormStepDatabaseAccount extends FormStep
  constructor: () ->
    @stepName = 'Set Up a Database User'
    @templateName = 'tmpl-nds-form-database-account'
    @expectedStepsLeft = 2

    @dbUsername = ko.observable('')
    @dbPassword = ko.observable('')
    @dbName = ko.observable('')

  getFormErrorMessage: =>
    if _.isEmpty @dbUsername()
      return "You must enter a database username!"
    if _.isEmpty @dbPassword()
      return "You must enter a database password!"
    if _.isEmpty @dbName()
      return "You must enter a database name!"

  extendFormData: (data) =>
    data.dbUsername = @dbUsername()
    data.dbPassword = @dbPassword()
    data.dbName = @dbName()

  constructNextStep: () =>
    dsEvents.dbacc.chain dsEvents.dbtype
    return new FormStepDataSourceName()


class FormStepCsvChoose extends FormStep
  constructor: ->
    @stepName = 'Select CSV files'
    @templateName = 'tmpl-nds-form-csv-choose'
    @expectedStepsLeft = 3

    @csvFile = ko.observable null

  getFormErrorMessage: =>
    unless @csvFile()
      'You must select a file to upload!'

  extendFormData: ->

  constructNextStep: =>
    dsEvents.csvchoose.chain dsEvents.dbtype
    new FormStepCsvUpload @csvFile()


class FormStepCsvUpload extends FormStep
  constructor: (@fileList) ->
    @plural = if @fileList.length > 1 then 's' else ''
    @stepName = "Uploading your file#{@plural}..."
    @templateName = 'tmpl-nds-form-csv-upload'
    @expectedStepsLeft = 2

    @error = ko.observable ''
    @currentFile = ko.observable 0
    @progress = ko.observable 0
    @size = ko.observable(-1)
    @complete = ko.computed =>
      @progress() is @size()

    _.each [@progress, @size], (x) ->
      x.disp = ko.computed ->
        _x = x()
        while _x >= 1000
          _x /= 1000
        _x.toPrecision 3
      x.units = ko.computed ->
        _x = x()
        if _x > 1000000
          if _x > 1000000000
            'GB'
          else
            'MB'
        else if _x > 1000
          'KB'
        else
          'B'

    @progressText = ko.computed =>
      progUnits = @progress.units()
      sizeUnits = @size.units()

      if progUnits is sizeUnits # Don't show 3.2KB / 5.6KB, just 3.2 / 5.6KB
        progUnits = ''

      @error() or
        if @size() > 0
          "File #{@currentFile() + 1} of #{@fileList.length}: #{@progress.disp()}#{progUnits} / #{@size.disp()}#{sizeUnits}"
        else
          'Calculating upload size'

    @progressWidth = ko.computed =>
      ((100 * @progress() / @size()) + @currentFile()) / @fileList.length

    @startUpload()

  prevStep: ->
    @stopUpload()

  returnToStep: ->
    @startUpload()

  uploadFileByNumber: (num, cb) ->
    file = @fileList[num]
    @progress 0
    @size file.size

    if @size() > 1 * 1024 * 1024
      return @error 'Your file is too large. The current maximum file size is 1MB.'

    doRequest = =>
      @uploadRequest = serverApi.sendFile "/upload/upload-file/#{@key}/#{num}", file,
        (err, resp) =>
          if err
            console.error err
            return @error "An error occurred while uploading your file#{@plural}."
          switch resp.status
            when 'success'
              cb()
            when 'error'
              console.error resp.error
              return @error "An error occurred while uploading your file#{@plural}."
      , (sent, total) =>
        @progress sent
        if total >= 0
          @size total

    if @key
      doRequest()
    else
      serverApi.sendPost '/upload/get-key', @data,
        (err, resp) =>
          if err
            console.error err
            return @error 'An error occurred contacting the server.'

          unless (@key = resp?.key)?
            return @error 'Unable to upload dataset.'

          doRequest()

  startUpload: ->
    @currentFile 0
    doUpload = =>
      @uploadFileByNumber @currentFile(), =>
        @currentFile @currentFile() + 1
        if @currentFile() < @fileList.length
          doUpload()
        else
          dsEvents.nextstep.trigger()
    doUpload()

  stopUpload: ->
    if @uploadRequest
      try
        @uploadRequest.abort()
      catch err
        console.error err

  backBtnText: 'Cancel Upload'
  nextBtnText: ''

  extendFormData: (data) ->
    data.key = @key

  constructNextStep: =>
    new FormStepCsvClean @key, @fileList.length


class FormStepCsvClean extends FormStep
  constructor: (@key, @numTables) ->
    @stepName = 'Verify your data'
    @templateName = 'tmpl-nds-form-csv-clean'
    @expectedStepsLeft = 1

    @tblIndex = ko.observable 0
    @isNextTableEnabled = ko.computed =>
      @tblIndex() < (@numTables - 1)
    @isPrevTableEnabled = ko.computed =>
      @tblIndex() > 0

    @tableSettings = (new CsvCleanTable(@key, i) for i in [0...@numTables])

    @curTable = ko.computed =>
      @tableSettings[@tblIndex()]

    @slickRows = ko.computed =>
      @curTable().slickRows()
    @slickColumns = ko.computed =>
      @curTable().slickColumns()

  nextTable: =>
    if @isNextTableEnabled()
      @tblIndex @tblIndex() + 1

  prevTable: =>
    if @isPrevTableEnabled()
      @tblIndex @tblIndex() - 1

  extendFormData: (data) ->
    data.validated = true

  asyncFormValidate: (callback) =>
    data = tables: ({
      hasHeader: tbl.hasHeader.value()
      delimiter: tbl.delimiter.value()
      rowsToKeep: tbl.rowsToKeep()
      types: tbl.overriddenTypes
      columnNames: tbl.overriddenNames
      tableName: tbl.tableName()
    } for tbl in @tableSettings)

    serverApi.sendPost "/upload/clean/csv/#{@key}", data,
      (err, resp) =>
        if err
          console.error err
          callback 'An error occurred contacting the server'
          return

        switch resp.status
          when 'success' then callback true
          when 'error'
            callback resp.error

  constructNextStep: =>
    new FormStepDataSourceName()


impute = (values) ->
  date = 0
  num = 0
  length = 0
  for value in values
    if not value? or value is undefined or value is null
      continue
    length++
    # check if it's a number
    if not isNaN(value) or not isNaN value.replace(/\$|\,/g,'')
      num++
    # check if it's a date
    m = moment(value)
    if m? and m.isValid()
      date++
  if num > 0.95 * length
    return 'num'
  if date > 0.95 * length
    return 'date'
  return 'cat'

class CsvCleanTable
  constructor: (@key, @index) ->
    @tableName = ko.observable "Table #{@index + 1}"

    @hasHeader = new Selector 'has-header', true, [true, false], ['Yes', 'No']
    @delimiter = new Selector 'delimiter', ',', ['\t', ';', ','], ['Tab', 'Semicolon', 'Comma']

    @rowsToKeep = ko.observable ''

    @slickRows = ko.observable []
    @header = ko.observable []

    @imputedTypes = ko.computed =>
      rows = @slickRows()
      impute _.pluck rows, col for col in @header()

    @overriddenNames = []
    @overriddenTypes = []

    @displayNames = ko.computed =>
      header = @header()
      @overriddenNames[i] or header[i] for i in [0...header.length]
    @dataTypes = ko.computed =>
      imputed = @imputedTypes()
      @overriddenTypes[i] or imputed[i] for i in [0...imputed.length]

    @slickColumns = ko.computed =>
      ((idx) =>
        new SlickColumn(
          name,
          type,
          (newName) =>
            @overriddenNames[idx] = newName
          , (newType) =>
            @overriddenTypes[idx] = newType
        )
      )(i) for [name, type], i in _.zip @displayNames(), @dataTypes()

    ko.computed =>
      data = # Subscribe to the necessary observables
        hasHeader: @hasHeader.value()
        delimiter: @delimiter.value()
        rowsToKeep: @rowsToKeep()
        types: @overriddenTypes
        columnNames: @overriddenNames
        tableName: @tableName.peek()

      serverApi.sendPost "/upload/preview/csv/#{@key}/#{@index}", data,
        (err, resp) =>
          if err
            console.error err
            TOAST.raise 'An error occurred contacting the server'
            return
          switch resp.status
            when 'success'
              @slickRows resp.rows
              @header resp.header
            when 'error'
              console.error resp.error
              TOAST.raise 'An error occurred while processing your file'

class SlickColumn
  constructor: (name, type, nameFn, typeFn) ->
    @name = ko.observable name
    @field = name
    @dataType = ko.observable type

    @name.subscribe nameFn
    @dataType.subscribe typeFn

  changeDataType: ->
    @dataType {cat: 'num', num: 'date', date: 'cat'}[@dataType()]


class FormStepGAProfileId extends FormStep
  constructor: () ->
    @stepName = 'Choose a Google Analytics Profile'
    @templateName = 'tmpl-nds-form-gaprof'
    @expectedStepsLeft = 2

    @gaId = ko.observable ''

  getFormErrorMessage: =>
    if not _.isEmpty @gaId() and /^\s*\d+\s*$/.exec @gaId() is null
      return "The profile ID you have entered is invalid."

  extendFormData: (data) =>
    if _.isEmpty @gaId() then @gaId '0'
    match = /^\s*(\d+)\s*$/.exec @gaId()
    if match? then data.gaId = match[1]
    else @getFormErrorMessage()

  constructNextStep: () =>
    # TODO: Add associated event
    return new FormStepDataSourceName()


class FormStepDataSourceName extends FormStep
  constructor: () ->
    @stepName = 'Set a Display Name'
    @templateName = 'tmpl-nds-form-name-ds'
    @expectedStepsLeft = 1

    @name = ko.observable('')

  getFormErrorMessage: =>
    if _.isEmpty @name()
      return 'You must enter a data source display name!'

  extendFormData: (data) =>
    data.name = @name()

  constructNextStep: () =>
    dsEvents.name.chain dsEvents.dbtype
    return new FormStepComplete()


class FormStepComplete extends FormStep
  constructor: () ->
    @stepName = 'Adding Your Data Source...'
    @templateName = 'tmpl-nds-form-complete'
    @expectedStepsLeft = 0

    @state = ko.observable('connecting')
    @errorMessage = ko.observable(null)

  initDOM: (dom, data) =>
    serverApi.sendPost '/data-source/create', data, (err, resp) =>
      if err
        console.error err
        if err.message
          @errorMessage(err.message)
          @state('knownError')
        else
          @errorMessage("An error occurred.")
          @state('unknownError')
      else
        if resp.key
          window.location = "/home?newDataSourceKey=#{encodeURIComponent(resp.key)}"
        else if resp.redirect
          window.location = resp.redirect


class Selector
  constructor: (@name, def, opts, labels) ->
    @_value = ko.observable opts.indexOf(def) ? def
    @value = ko.computed
      read: =>
        opts[@_value()]
      write: (val) =>
        @_value opts.indexOf(def) ? val
    @options = ({
      label: l
      value: i
    } for l, i in labels)


module.exports = DataSourceFormView
