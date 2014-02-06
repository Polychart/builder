# Import modules that are needed
request = require 'request'
express = require 'express'

# Create a web application using the `express` framework
app = express()

# Automatically parse HTTP request bodies that contain JSON
app.use express.bodyParser()

# Serves all files in the current directory.
# A real application would be more cautious about what files
# are accessible.
app.use express.static __dirname

# Listen for GET requests to '/'
app.get '/', (httpRequest, httpResponse) ->
  # Redirect the browser to the `/custom_backend_example.html`
  # See the file of the same name in the current directory.
  # This file contains all of the client-side code needed to 
  # initialize the dashboard building with a custom backend.
  httpResponse.redirect '/custom_backend_example.html'

# Listen for POST requests to '/data-source'
# Look at `custom_backend_example.html` to see when and how
# these requests are sent.
app.post '/data-source', (httpRequest, httpResponse) ->
  # Get the body of the HTTP request
  # The express framework automatically converts the JSON
  # to a JavaScript object.
  dataSourceQuery = httpRequest.body

  # At this point, a real application would check that
  # the current user is allowed to access the data source
  # specified in the query.
  # `dataSourceQuery.dataSourceKey` matches a data source
  # key that was specified in the Query service configuration
  # file.

  # Send an HTTP request to the Query service.
  # The body of HTTP request we received from the client
  # is re-encoded into JSON before being sent to the Query
  # service.
  request {
    method: 'POST'
    url: 'http://localhost:3681/data-source'
    json: dataSourceQuery
  }, (err, queryRes, body) ->
    # Check if something went wrong with the query.
    # It is recommended that responses with an HTTP status
    # code other than 200 be logged, but not sent to the
    # client.
    if err or queryRes.statusCode isnt 200
      # Log the response from the Query service,
      # since an error occurred.
      console.error err
      console.error body

      # Send an error response to the client.
      httpResponse.status 500
      httpResponse.send JSON.stringify {message: 'Query error'}
    else
      # The query was successful.
      # Send the query result back to the client.
      httpResponse.send JSON.stringify body

# Run an HTTP server on port 3010.
app.listen 3010
