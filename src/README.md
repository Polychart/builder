Herein lies the frontend source code for the Polychart Dashboard Builder. The
directory `poly/main` contains the source code to UI of the Dashboard Builder.
The `poly.coffee` file defines the API for constructing the Dashboard Builder
and constituents; the API is as follows:

Polychart Dashboard Builder API
===============================

`poly.dashboard`:
  This function consumes an object `params` that contains the following fields:
  * `params.header`: `bool`
    Flag indicating whether or not the header should be shown; default is
    `true`.
  * `params.local`: `bool`
    Flag that disables saving and tutorial completion server calls.
  * `params.customSaving`: `function`
    An optional function that overrides the default saving behaviour (an HTTP
    request).  The function is passed a serialized dashboard.
  * `params.isDemo`: `bool`
    Flag to use demo data and to disable features such as saving; default is
    `false`.
  * `params.showTutorial`: `bool`
    Flag indicating whether or not the NUX tutorial is to be shown; default is
    `false`.
  * `params.width`: `string | num`
  * `params.height`: `string | num`
    Either a numerical amount indicating the pixel or percent dimensions of the
    dashboard builder or the string `fill`.
  * `params.key`: `string`
    A unique key identifying a dashboard. If `params.customSaving == true`, then
    this is optional.
  * `params.name`: `string`
    A string denoting the name of the dashboard; this will correspond to the
    string shown in the title field of the dashboard builder.
  * `params.dom`: `string | DOM`
    Either a string corresponding to the `id` of the `DOM` on which the
    Dashboard Builder is to be rendered on, or the `DOM` element itself.
  * `params.dataCollection`: `list | object`
    A list of JSON objects (or just one) with fields `type`, `dataSourceKey`
    and `tableNames` for which the dataview should be populated with.
  * `params.initial`: `list`
    A list of JSON objects, each of which are serialized states of the
    dashboard. If this list is nonempty, then the serialized items are passed
    into the constructor, and the dashboard will initially be populated by the
    deserialized versions of those objects.

`poly.dashviewer`:
  This is a constructor for the Dashboard Viewer, an interface in which charts
  may be viewed but not edited. This function consumes an object `params` with
  the following fields, each of which have the same meaning as above:
  * `params.name` : `string`
  * `params.initial`: `list`
  * `params.dom`: `string | DOM`
  * `params.dataCollection`: `list`

`poly.chartbuilder`:
  Constructs only the Chartbuilder interface, and nothing more. This function
  consumes an object `params` with the following fields, each of which has the
  same meaning as above:
  * `params.header`: `bool`
  * `params.isDemo`: `bool`
  * `params.width`: `string | num`
  * `params.height`: `string | num`
  * `params.initial`: `list`
  * `params.dom`: `string | DOM`
  * `params.dataCollection`: `list`

`poly.chartviewer`:
  Constructs a viewer interface for a single chart. This function consumes an
  object `params` with the following fields, each of which have the same meaning
  as above:
  * `params.width`: `string | num`
  * `params.height`: `string | num`
  * `params.initial`: `list`
  * `params.dom`: `string | DOM`
  * `params.dataCollection`: `list`

`poly.data`:
  A function to construct a Polychart data source. This takes an object `args`
  with the following fields:
  * `args.type`: `string`
    This denotes the type of data source to be constructed. This can be `local`
    or `remote`.
  * `args.tables`: `list`
    A list of tables---the data.
  * `args.customBackend`: `bool`
    A flag indicating whether or not a custom backend is to be used; that is,
    one which denotes whether or not the Polychart backend is used.
  * `args.dataSourceKey`: `string`
    A unique identifier for a backend data source.
