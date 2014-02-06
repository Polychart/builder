<!DOCTYPE html>
<article>

Polychart OEM
=============

Polychart offers a dashboard building package that you can integrate into your
web application.  You can see this package in action on our website at
[https://www.polychart.com/demo](https://www.polychart.com/demo).

Getting started
---------------

Be sure to have [Python 2.7](http://python.org/download/) installed before
proceeding.

Navigate to this directory at a command-line, then run the following command:

    python -m SimpleHTTPServer

You can now run the example files in your browser by visiting
[http://localhost:8000/](http://localhost:8000/).  `dashbuilder_example.html`
is a great place to start.

Integrating Polychart into your application
-------------------------------------------

1. Serve the files in the `static` directory at the URL `/static`.
2. Include the necessary files in any page that integrates Polychart:

        <link rel="stylesheet" href="/static/common/dependencies.css">
        <link rel="stylesheet" href="/static/main/main.css">

        <script src="/static/common/dependencies.js"></script>
        <script src="/static/main/main.js"></script>

3. Add a target element to the body:

        <div id="dashboard"></div>

4. Initialize Polychart:

        <script>
          var poly = require('poly');
          poly.dashboard({
            dom: $('#dashboard')[0],
            ...
          });
        </script>

    To understand the parameters required for initialization take a look at the
    example files and the following section.

API Documentation
-----------------

The Polychart OEM package provides four components: the dashboard builder
(`poly.dashboard(...)`), the dashboard viewer (`poly.dashviewer(...)`), the
chart builder (`poly.chartbuilder(...)`), and the chart viewer
(`poly.chartviewer(...)`).

All of these functions require an object containing the following fields:

 - `dom`: Either the DOM element to render to, or a string matching the ID of
   an element.
 - `width`: A number of pixels, or a string in the form "x%" (percentage
   value).
 - `height`: A number of pixels, or a string in the form "x%" (percentage
   value).
 - `dataCollection`: An object with the following fields:
   - `type`: 'local'
   - `tables`: An array of Table objects, described below.
 - `initial`: The initial state of the chart or dashboard to show after loading.
   This should be the object that was provided by calling the serialize method
   of one of the builders, or via the `customSaving` mechanism.

Components:

 - `poly.dashboard(...)`

    Shows the full Polychart dashboard building interface, allowing the user to
    create and arrange a dashboard containing charts, numbers, and tables.

    Additional parameters: 
     - `name`: A user-editable name for the dashboard.
     - `local`: True when data processing happens clientside.
     - `customSaving` (optional): A function that is called with the current
       state of the dashboard whenever a save is required.

    Returns an object with a single method `serialize()` that returns the
    current state of the dashboard.

 - `poly.dashviewer(...)`

    Shows a Polychart dashboard without the editing interface.

    Additional parameters: 
    - `name`: A name for the dashboard.

 - `poly.chartbuilder(...)`

    Shows the Polychart chart building interface, allowing the user to create
    complex chart using simple drag and drop.

    No additional parameters.

    Returns an object with a single method `serialize()` that returns the
    current state of the chart.

 - `poly.chartviewer(...)`

    Shows a single chart without the editing interface.

    No additional parameters.

A Table object has the following fields:

 - `name`: Name of the dataset
 - `data`: An array of homogenous objects.  Example:

        [
          {age: 13, name: "John"},
          {age: 17, name: "Sarah"},
          ...
        ]

 - `meta`: An object containing additional information about each column of the
   table.  The keys of the object match the names of columns in the table (e.g.
   "age" and "name" in the above example).  Each column must have a `type`
   field that is one of "number", "date" and "cat" (category).  Columns of type
   "date" must also have a `format` field that specifies the date/time format
   in moment.js format.  Example:

        {
          sales: {
            type: "number"
          },
          date: {
            type: "date",
            format: "YY-mm-dd"
          },
          agentName: {
            type: "cat"
          }
        }

Setting up the Polychart Query service (optional)
-------------------------------------------------

The examples in `dashbuilder_example.html`, `chartbuilder_example.html`, and
`chartviewer_example.html` provide the entire data set to the Polychart package
in the initialization step.  This is straightforward and works well for smaller
data sets, but becomes more cumbersome with larger amounts of data.  For larger
data sets, Polychart provides an optional Query package that generates SQL
queries based on what is needed to render a chart.  To use this package:

1. Write a configuration file.

    The Query service requires a configuration file written in JSON that defines
    a list of data sources.  You must specify a unique key for each data source
    (only alphanumerical characters, hyphens, and underscores are permitted).

    An example configuration file:

        {
          "data_sources": {
            "my-sales-database": { // The unique key for this data source
              "type": "mysql", // Also supported: "postgresql", "infobright"
              "connection_type": "direct", // Required
              "db_name": "sales", // "CREATE DATABASE sales"
              "db_host": "localhost",
              "db_port": 3306,
              "db_username": "polychartsales",
              "db_password": "secret"
            }
            // More data sources can go here
          }
        }

    Note: it is recommended that the database user account be limited to
    read-only access on the tables it needs.

2. Run the HTTP service.

    1. Install the required dependencies.  On Ubuntu:

            sudo apt-get update
            sudo apt-get install python-dev python-pip libmysqlclient-dev libpq-dev
            sudo pip install --upgrade distribute
            sudo pip install python-dateutil MySQL-python psycopg2

    2. Place the `polychartQuery` package on a server.

    3. Set the environment variable `PYTHONPATH` to the absolute path of the
       *parent* directory of the package.  For example, if the package is
       placed in `/a/b/c/polychartQuery`, set `PYTHONPATH` to `/a/b/c`.

    4. Choose an unused TCP port number on your server (the rest of this guide
       will assume `3681`).

    5. Ensure that your server firewall is properly configured to **disallow**
       connections to that port.

    6. Start the service using the command
       `python2 polychartQuery/httpService.py <CONFIG_FILE_PATH> <PORT_NUMBER>`.

3. Add request handlers to your application that receive requests from
   JavaScript and forward them to the Query service as needed.

    The implementation of this step depends significantly on what language and
    framework your application is written in.
 
    To use the Query service, send a POST request to
    `http://localhost:3681/data-source`.  The body of the request should be a
    JSON encoded object.  This object is provided to your application via
    JavaScript, as documented in step 4.
 
    Your application may wish to inspect and/or validate the query.  Each query
    object contains the fields "dataSourceKey" and "command".  Most applications
    will want to check that the current user is allowed to access the specified
    data source.
 
    The following commands are available:
 
    - `listTables`
    - `getColumnMetadata`
    - `queryTable`
 
    It is not necessary to understand the details of these commands, as the
    queries will be generated by the Polychart package.
 
    It may be helpful to view an example implementation of this step.  In the
    file `packageExamples/custom_backend_example.coffee`, this step is
    implemented using Node.js and Express, which may be helpful regardless of
    the language of your application.

4. Initialize the JavaScript package with the appropriate configuration.

    This section assumes that you have successfully initialized the Polychart
    dashboard building interface using `poly.dashboard(...)` (described in
    previous sections).

    - Provide a `dataCollection` of type `remote`, not `local`:
 
            poly.dashboard({
              // ...
              dataCollection: {
                type: 'remote',
                dataSourceKey: 'my-data'
              }
            })
 
    - Add a `customBackend` implementation that uses the request
      handlers from step 3.
 
            poly.dashboard({
              // ...
              dataCollection: {
                type: 'remote',
                dataSourceKey: 'my-data',
                customBackend: function (query, callback) {
                  // `query` is an object that contains "dataSourceKey",
                  // "command", etc.
 
                  // Send this query to the request handlers from step 3
 
                  // Invoke the callback when the query returns
                  if (querySucceeded) {
                    callback(null, queryResult);
                  } else {
                    callback(queryErrorDetails);
                  }
                }
              }
            })

    An example implementation of this step is provided in the file
    `packageExamples/custom_backend_example.html`.  This example is compatible
    with the Node.js example provided in step 3.

</article>

<style>
@import url("https://fonts.googleapis.com/css?family=Source+Sans+Pro:400,200,300,600,700,400italic");

article {
  font-family: 'Source Sans Pro', sans-serif;
  font-size: 16px;
  font-weight: 400;
}

article h1 {
  margin: 0;

  font-size: 44px;
  font-weight: 200;
}

article h2 {
  margin: 0;

  font-size: 30px;
  font-weight: 300;
}

article a {
  color: #44A;
  text-decoration: none;
}

article a:hover {
  text-decoration: underline;
}

article strong {
  font-weight: 600;
}

article code {
  color: #444;
  font-size: 14px;
}

article pre {
  margin-left: 30px;
}
</style>
