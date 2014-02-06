makeRequest = (path, data, callback, config) ->
  callback or= ->

  $.ajax "/api#{path}", _.extend {
    data
    dataType: 'json'
    headers:
      'X-CSRFToken': Cookies.read('csrftoken')
    success: (data, textStatus, req) ->
      callback null, data
    error: (req, textStatus, errorThrown) ->
      err =
        httpStatus: req.status
        message: textStatus

      contentType = req.getResponseHeader('Content-Type')
      contentType = contentType and $.trim(contentType.split(';')[0])
      if contentType is 'application/json'
        responseBody = JSON.parse req.responseText
        err.message = responseBody.message

      callback err
  }, config

sendGet = (path, params, callback) ->
  request = makeRequest path, params, callback

  abort: ->
    request.abort()

sendQueryPost = (path, params={}, callback) ->
  request = makeRequest path, params, callback,
    type: 'POST'

  abort: ->
    request.abort()

sendPost = (path, body, callback) ->
  body or= {}

  request = makeRequest path, JSON.stringify(body), callback,
    type: 'POST'
    processData: false

  abort: ->
    request.abort()

sendFile = (path, file, callback, onProgress) ->
  onProgress or= ->

  request = makeRequest path, file, callback,
    type: 'POST'
    contentType: file.type
    processData: false
    # http://www.dave-bond.com/blog/2010/01/JQuery-ajax-progress-HMTL5/
    xhr: ->
      xhr = new XMLHttpRequest()
      xhr?.upload?.addEventListener 'progress', (evt) ->
        onProgress evt.loaded, if evt.lengthComputable then evt.total else -1
      , false
      xhr

  abort: ->
    request.abort()


module.exports = {sendGet, sendQueryPost, sendPost, sendFile}
