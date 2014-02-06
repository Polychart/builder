Polychart Query package
=======================
Translating the query specification produced by the frontend code and
subsequently retrieving and formatting the data from an external data source
are two of the largest backend tasks for the Polychart Dashboard Builder.
Luckily, much of the code is independent of the remaining functionality
required by the backend server, and thus these particular data source tasks may
be factored out into standalone components. The Polychart Query package is our
implementation of these processes: the package, given information about the
data source, may be passed in a frontend query specification, do internal
processing, and return the resulting data in a form understandable by the
Dashboard Builder.

In the case that a Python backend is used, the Polychart Query package may be
directly included as an extra module to handle data sources, query
specifications and formatting results. If, on the other hand, the backend is
implemented in a language that does not talk directly to Python, this package
provides the module `httpService.py` which, when run, provides the
functionality of the package over HTTP.

Data Source Connection Interface
================================
The basic object provided by this package is the `Connection` object. This
represents a connection from the Dashboard Builder to some data source, may it
be a MySQL data base, PostgreSQL data base, or Google Analytics
account. The methods that the `Connection` object provides give an interface to
obtain information about tables present in a data source, obtain metadata about
a column and to query the table. The specifics of these functions will be
detailed presently.

**Note.** The interface provided by the `Connection` object is the same as the
interface provided by the HTTP service through the path `/data-source` and the
appropriate `command`.

`Connection.listTables`
-----------------------
Tables of the data source are provided in a list.

Each entry in this list will be a JSON object or Python dictionary which has the
keys `name`, with value being the name of the table, and `meta`, whose value is
a JSON object or Python dictionary. The object in the `meta` value will have
keys corresponding to names of columns within the given table, and the value
will be an object containing the field `type` and a value denoting the data type
of this column.

For example, a call to `Connection.listTables` may result in the following:

```
>>> Connection.listTables()

> [ { "name": "Table One",
      "meta": { "Column One": { "type": "date" },
                "Column Two": { "type": "num"  }}},
    { "name": "Table Two",
      "meta": { "Column Three": { "type": "cat" },
                "Column Four" : { "type": "num" }}}]
```

`Connection.getColumnMetadata`
------------------------------
Provided a table name, column name and data type for the specific column,
returns a Polychart2.js meta data item. The primary use for this method is to
obtain the range information for a given column, which is used for filters.

This method expects the following parameters:

  * `tableName`: `string`
    The name of the table containing the target column.
  * `columnName`: `string`
    The name of the column whose meta data is required.
  * dataType`: `string`
    The data type of the column to be queried. Must be one of the following
    three strings: `cat`, `date`, or `int`. This is required since the query for
    each data type is different.

If this method is called from the HTTP service, then these parameters are
expected to be included in the body of the HTTP request.

This method will return a meta data object, which will differ based on the data
type provided.

  * If `dataType == cat`, then returned will be an object with a key `values`,
    whose value will be list of different values within that column.
  * If `dataType == num`, then returned will be an object with keys `min` and
    `max`, and whose values correspond to the minimum and maximum numerical
    values that the column possess.
  * If `dataType == date`, then returned will be an object with keys `min` and
    `max` whose values will be Unix time stamps representing the minimum and
    maximum dates that occur within the column.

Example queries and results are as follows:

```
>>> Connection.getColumnMetaData("Table Two", "Column Three", "cat")

> { "values": ["Value One", "Value Two", "Value Three", ...] }

>>> Connection.getColumnMetaData("Table One", "Column One", "date")

> { "min": 137711000, "max": 1377540000 }

>>> Connection.getColumnMetaData("Table Two", "Column Four", "num")

> { "min": 3.1415926535897, "max": 42.0030937784 }
```

`Connection.queryTable`
-----------------------
Provided a table name, a query specification object and an optional limit,
returns data corresponding to the query defined in the query specification
object. The data returned will be formatted to work with Polychart2.js.

This method expects the following parameters:

  * `tableName`: `string`
    The name of the table to query on.
  * `querySpec`: `JSON object`
    This is a specification object generated by Polychart2.js. Roughly speaking,
    this contains information decribing which columns are selected, what
    filters to apply, any sorting or statistical transformation that needs to be
    done, and other relevant meta information. For more detail on the form of
    this, see `query.py`.
  * `limit`: `int`
    This number denotes the maximum number of rows of data to return from the
    query. This is optional, and the default is `1000`.

If this method is called from the HTTP service, then these parameters are
expected to be included in the body of the HTTP request.

The returned data will be a JSON object or Python dictionary, with two fields: a
field with key `data`, whose value is a list containing the resulting query
data, formatted for Polychart2.js; and a field `meta`, which is an object of
key-value pairs, describing meta data for individual columns.
