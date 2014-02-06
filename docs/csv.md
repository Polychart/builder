<!DOCTYPE html>
<article>

CSV data sources - overview
---------------------------

When a user prepares to upload a CSV data set, a PendingDataSource object is
created in the database, and this object's key is used to reference this data
set during upload. Files uploaded by the user are written directly to
`PROJECT_ROOT/uploadedData/raw/PENDING_DS_KEY-FILE_NUMBER`. The user is asked
to verify the CSV parsing settings (header yes/no, comma- or tab-separated,
etc). In addition, a preview of the first 100 parsed rows is provided as the
user changes settings. This preview is used by the frontend to determine the
most likely data type of each column (which the user can override).

The files are then parsed according to the provided settings and converted into
a JSON string in a format suitable for use with Polychart.js. This JSON string
is stored in the database, in a new LocalDataSource object. A new DataSource
object is created for the CSV file as well. The motivation behind creating a
separate table for JSON data is that large data sets might otherwise decrease
the efficiency of queries against the DataSource table.

When a user opens a dashboard with a DataSource whose type is local (currently,
only 'csv'), rather than providing a data source key for remote queries, the
frontend is provided with the raw data directly, in full. All further processing
is done entirely on the frontend by Polychart.js, without any queries to the
server. This functions largely the same as the /demo page, except that a
dashboard key is still provided to save the dashboard state as needed.



Events - overview
-----------------

The `src/poly/common/events.coffee` file contains utilities for the global event
bus. This bus is a wrapper around jQuery's event system, in order to support
events without a target element (by actually applying them to a pseudo-element).
To use it, the dashboard builder (or the website) events files pass it an "event
tree", which defines the names of events that will be used. Each event is a leaf
of this tree. For an example tree, see `src/poly/main/events.coffee`.

The tree is transformed so that each event leaf contains methods to trigger this
event, and to listen to it. An example usage might be the following:

    Events.ui.chart.add.on (event, params) ->
      ...

    Events.ui.chart.add.trigger(params)

Event listeners may also be registered at initialization from the
`defaultListeners` collection. For details, see `src/poly/common/events.coffee`.

Events in this tree can also be listened to and triggered on specific DOM
elements, rather than the pseudo-element, similar to the following:

    Events.ui.chart.add.onElem (elem, event, params) ->
      ....

    Events.ui.chart.add.triggerElem(elem, params)

The event bus also contains some rudimentary analytics support. The event tree
initialization defines an internal `_track` method, which tracks events using
Segment.io's `window.analytics`, if provided, and by the internal
`serverApi.sendPost`, if available. The event's name, and any tracked parameters
(see the event tree referenced above for details), are included automatically in
the tracking request.

To facilitate automatically tracking certain events, the provided event tree can
assign "default properties" to event leaves. On initialization, these default
properties are given to the `defaultPropHandler` function for each event.

In the case of `src/poly/main/events.coffee`, the `tracked` property is set to
true for events that should be tracked, or to an array of strings to define
specific params of the event that should be tracked. `defaultPropHandler` then
checks if this property is set, and registers a listener that calls the internal
`_track` method if they are. The properties are filtered down to those listed
in the array, to avoid logging, say, an entire chart specification when this is
not wanted.

In order to use these analytics features for user interaction, event leaves have
`trackClick`, `trackLink`, and `trackForm` methods, which take a DOM element and
register jQuery event listeners to the relevant click/submit events. When these
events are triggered, the internal `_track` method is called. This probably
should be refactored to call the registered listeners instead, but for now it
mimics the semantics of Segment.io's similarly-named methods.

Finally, in order to support rudimentary funneling, each time an event is fired,
it also includes a randomly-generated event ID, which is sent to the server if
the event is tracked. This ID is hashed with the user and session on the server
side, to help prevent collisions. In order to "group" or "chain" events, a
`chain` method exists on each event leaf, which has the same purpose as the
`trigger` method, except that it takes an additional parameter for which event
to chain it on (either by name, or by the actual event leaf object). The ID for
the newly-fired event will not be randomly-generated, but will instead be the
same as the most recent event of the provided type. This makes it possible to
create an explicit association between events.

</article>
