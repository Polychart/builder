Polychart Dashboard Builder
===========================
This directory contains all the frontend code defining the Polychart Dashboard
Builder. The flow of the code is roughly as such.

The entry points for the Dashboard Builder are defined in the `main/` directory,
where `dashbuilder.coffee` implements the primary entry point for the dashboard
builder itself. There, the initial configuration object is processed, views like
the `dataView`, `chartbuilderView`, `workspaceView`, and others are constructed,
initialized, and populated with any serialized states present in the
configuration object. Finally, events are initialized, and handlers are attached
to certain UI elements.

Data
----
From here, we split up into multiple parts. First, the `data/` directory
contains code for how the data is managed, used and passed around in the
Dashboard Builder. The entry point for all that is contained in
`dataView.coffee`, where a list of data sources is passed in, and the internal
`dataSource` objects are constructed; the intricacies of the `dataSource`
objects are implemented in `dataSource.coffee`.

After constructing the `dataSource` objects, the data panel is populated, in
accordance to the code in `tableView.coffee`. The data panel is populated with
items known as `metrics`. See the internals for more detail.

One last essential bit defined in `dataView.coffee` is the `tableMetaData`
object. This object shall be present in many of the other views, and is an
object where information about the data source may be gathered.

Dashboard
---------
Next, the `dash/` directory contains code implementing the main dashboard view,
along with the way items behave in the primary workspace. This view is
constructed in `dashboard.coffee`, in which the gridded `workspaceView` and the
left-hand panel `quickaddView` are constructed.

First, the `workspaceView` defines the behaviour of drag and drop items in the
gridded workspace. Events are initialized here to describe functions to invoke
when items are interacted with. Methods are also implemented here to serialize
and deserialize the Dashboard Builder's state.

The `quickaddView` defines the actions of the Quick Add menu pane. This panel
provides a simple interface for constructing common charts and dashboard items,
as well as a means of navigating among different interfaces wrapped in the
Dashboard Builder.

Finally, the `dash/` directory also contains code defining the behaviour of free
floating items in the workspace. See the directory `dash/item/` for more detail.

Charts/Numerals/Tables
----------------------
Besides the primary DashboardView, there are currently three other main
interfaces to the Dashboard Builder: the Chart Builder, the Table Builder and
the Numeral Builder. As their names describe, each interface provides
specialized tools for constructing charts, numerals, and tables, respectively.
The basic structure of each is roughly the same, so only the structure of the
Chart Builder will be described here.

The entry point to the Chart Builder is found in `chartbuilder.coffee`.
Initialization and construction are two different stages to the process: the
Chart Builder View itself is constructed upon loading up the Dashboard Builder,
but the model is not populated until it is initialized upon actual launching.
The construction process initializes state variables; the initialization takes
place when the `ChartbuilderView.reset` method is called. The `reset` method
takes a configuration object, one whose primary field of concern is
`params.spec`. The value of `params.spec`, if any at all, is a Polychart2.js
chart specification object, and defines the initial state of the Chart Builder;
if `params.spec` is not present, then the Chart Builder starts empty.

The workings of the Chart Builder are then split up to several modules. The
first is the view dealing with `layers`. Layers are objects that, given metric
objects corresponding to data, produce the abstract relationships that will
eventually define the visual components to the chart. Briefly speaking, this is
done by associating each metric to some aesthetic, being position coordinates,
size scales or colour scales, and from which a corresponding Polychart2.js
specification is produced. See `layer.coffee` for more detail.

Moving on from layers, we have the Filters View. This defines the interface for
defining filters on the whole chart. Currently, the filters act on all layers
present in the chart. On a high level, filters work by querying extended meta
information from the data source, from which a notion of range is obtained. With
this range, the filters view is able to display either a slider or dropdown menu
from which the user may filter out certain values in the range. This is then
translated into the corresponding Polychart2.js specification, and rendered
accordingly. See `filter.coffee` for more detail.

Joins come next. Joins allow a user to visualize data coming from different
tables. The model for joins is a graph where tables are vertices and joins are
edges. There are two modes available for joins: basic mode and advanced mode.
In the basic mode, the `joinsView` model checks whether or not there are tables
that are not connected in the joins graph, and prompts the user to add
unconnected tables. In the advanced mode, the user has the ability to add or
remove arbitrary joins.

Then, there is the Advanced Panel. A collection of toggles and options are
located here, that do not fit anywhere else. The options to define facets and
change the coordinates, for example, are implemented here. Data is passed in and
transformed into the corresponding Polychart2.js specification, as usual.

Finally, the directory `chart/aes/` defines the behaviour of *aesthetics*, which
are the visual elements of a chart such as the position of a data mark, the
colour of a mark and the size of a mark. More precisely, the code controlling
how layers transform them into the corresponding Polychart2.js specification is
located here.

Misc
----
Other files that are located in this directory include

  * `anim.coffee`: An internal library to display rudimentary animations; mainly
    used for the NUX tutorials.
  * `bindings.coffee`: This defines custom bindings to Knockout.js, which are
    useful in various UI elements, such as Dropdown Menus.
  * `dnd.coffee`: A Drag-and-Drop binding to jQuery UI.
  * `const.coffee`: A collection of constants used throughout the codebase.
  * `overlay.coffee`: Certain custom UI elements are implemented through a
    global overaly on top of the Dashboard Builder. For instance, a Dropdown
    Menu is faked constructing a floating DOM element which holds the names of
    options associated with the dropdown. Dialogue boxes are also defined here.
  * `parser.coffee`: A small parser used to extract things like metric names,
    statsistics used, and bin widths.
  * `events.coffee`: Instantiation of the event bus within the Dashboard
    Builder.
  * `init.coffee`: A file that is required before starting any other scripts, in
    order to initialize things like Knockout.js templates and custom bindings.
  * `header.coffee`: Code that wires up the header.
  * `share.coffee`: Code that wires up the share panel.

And of course, many styles to prettify the Dashboard builder.
