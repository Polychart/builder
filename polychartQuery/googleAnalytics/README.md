Google Analytics Data Source
============================
The Google Analytics is an OAuth data source. See `oauth.md` for general details
pertaining to OAuth data sources. Here, we shall discuss the specifics regarding
to the Google Analytics implementation. There are three files in this directory,
each of which are outlined now.

Before proceeding, it would be prudent to touch on the peculiarities of Google
Analytics as a data source, so that some of the design choices are clear. First
of all, there is a notion of **metrics** and **dimensions** in Google Analytics.
Essentially, metrics are numbers and dimensions are everything else. Now, since
most data that we care about is in numbers, Google Analytics requires at least
one metric per request. This will shape some of the implementation below.

Another thing is that much data requested from Google Analytics is naturally
connected with time. For example, the number of visitors on a site is, for many
cases, queried with time as a dimension. Thus, for user convenience, a `time`
dimension is artificially inserted into each table. However, `time` is **not** a
valid dimension for Google Analytics; instead, they offer more specific time
steps, such as `date`, `year`, `month`, and so on. The translation between the
general dimension `time` to the specific dimensions that Google Analytics
expects is performed in the query building stage, and relies on any binning
present on the dimension.

`params.py`
-----------
This file contains some parameters that are constant with all Google Analytics
data source instances. This includes the list of possible dimensions and metrics
provided by Google Analytics and the primary endpoints for accessing data.  As
noted above, each table has a `time` dimension artificially inserted.

`connection.py`
---------------
The Connection object representing a Google Analytics connection is implemented
here. In particular, the standard methods `listTables`, `getColumnMetadata` and
`queryTable` are defined here.

The `listTables` method here simply calls the `GAParams.getTables()` method to
get a static list of tables. This also checks whether or not the user has
ecommerce options on, and includes or rejects those tables as appropriate.

The `getColumnMetadata` method is a bit more hacky. If the column for which
meta data is requested happens to be a metric, then there are no problems with
simply querying for data on that column. However, if the column in question is a
dimension, then we include the `visitors` metric into the query to construct a
valid request. Note that the choice of the `visitors` metric was arbitrary. The
returned data is processed accordingly to obtain the range meta data.

Much of the work done for `queryTable` is implemented in the query translator
found in `query.py`. See the below section for details.

`query.py`
----------
The query translator for Google Analytics is implemented here. A majority of the
code is dedicated to formatting the response obtained from Google Analytics. One
aspect to this query translator that is particular to Google Analytics is that
the name of columns cannot have the usual `tableName.columnName` form, since
there really is no notion of tables in Google Analytics. Thus some processing
must be done in that regards.

Another idiosyncrasy of Google Analytics is that filtering for dimensions is
rather painful: you must provide either a list of values to match or build a
regular expression that matches the desired dimensions. The current method is to
simply build the list of values requested, but this is extremely inefficient and
should be much improved.

Yet another developer obstacle is introduced by the `time` dimension sugar
mentioned before. Since this `time` dimension is a construct of convenience, we
must translate it to some combination of `date`, `hour`, `day`, `week`, `month`,
and `year` in order to obtain the correct data. This is implemented in the
binning functions. If no binning is attached to the `time` dimension, then we
query for `date`.

Finally, a word on processing and formatting the returned data. The most work is
involved in the case where `time` has been queried. When there is binning, we
must manually aggregate the data into the appropriate bin sizes, and relabel the
data fields in the resulting data. This is done in the huge `_formatTimeData`
function found near the bottom of the file.
