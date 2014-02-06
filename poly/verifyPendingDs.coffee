serverApi = require('poly/common/serverApi')

load = (dsParams) ->
  serverApi.sendPost '/data-source/create', dsParams, (err, response) ->
    if err
      console.error err
    else
      window.location.href = '/home'

module.exports = {run}
