Events                    = require('poly/main/events')
serverApi                 = require('poly/common/serverApi')

tutorial = (local) ->
  [
    {
      cover: '.container'
      title: 'Your First Dashboard'
      msgs: 'Welcome to the tutorial. We\'ll show you how to use the dashboard builder by
working with two data sets: "User Data", and "Sales".'
      buttonText: 'Continue'
      onFinish: ->
        Events.ui.nux.firstdb.trigger()
      skippable: true
      ref: '.workspace-area'
      top: 20
      left: 15
    },
    {
      cover: 'HEADER, .content-panel'
      template: 'tmpl-nux-data-panel'
      title: 'The Data Panel'
      msgs: 'Here is where the data sets are displayed. The green buttons represent the columns in the data set.'
      instructions: [
        {text: 'Click the "View/Edit" button beside our first data set, "User Data"', event: Events.nav.datatableviewer.open},
      ]
      onFinish: ->
        Events.ui.nux.datapanel.trigger()
      ref: '.content-panel'
      top: 20
      left: 15
      arrowDir: 'left'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Data Table'
      msgs: 'We can see that this data set has 4 columns, including "signup_date", "gender", and "time_on_site", which we will work with.'
      instructions: [
        {text: 'After getting a sense of the data, click "Go Back" above', event: Events.nav.datatableviewer.close},
      ]
      onFinish: ->
        Events.ui.nux.datatable.trigger()
      ref: '.data-panel'
      top: 20
      left: 100
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .workspace-area'
      title: 'First Chart'
      msgs: 'Let\'s create our first chart! A bar chart of user signups per day should do!'
      instructions: [
        {text: 'Click the "Bar Chart" button', event: Events.ui.quickadd.expand},
        {text: 'Drag "signup_date" to "X Axis"', event: Events.ui.metric.add},
        {text: 'Drag "count(*)" to "Y Axis"', event: Events.ui.chart.add}
      ]
      onFinish: ->
        Events.ui.nux.chartspanel.trigger()
      ref: '.workspace-area'
      top: 110
      left: 15
      arrowDir: 'left'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Edit Chart'
      msgs: 'This chart shows the number of new users per day. You can edit it further in the chart builder screen.'
      instructions: [
        {text: 'Move your mouse over the chart and click "Edit Chart"', event: Events.nav.chartbuilder.open},
      ]
      onFinish: ->
        Events.ui.nux.workspace.trigger()
      ref: '.data-panel'
      top: 70
      left: 25
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .chart-container'
      title: 'Chart Builder'
      msgs: 'On the left here we see additional options for customizing your chart. For example, we can map other columns to, say, the colour of our bars.'
      instructions: [
        {text: 'Drag "gender" to "Color" to colour the bars based on gender.', event: Events.ui.chart.render},
      ]
      onFinish: ->
        Events.ui.nux.layerspanel.trigger()
      ref: '.chart-container'
      top: 190
      left: 15
      arrowDir: 'left'
    },
    {
      cover: 'HEADER, .chart-container'
      title: 'Chart Builder'
      msgs: 'Great! Now, notice how each bar covers a single day worth of data. We can change that.'
      instructions: [
        {text: 'Click "bin(signup_date, day)" on the "X Axis".', event: Events.ui.dropdown.show},
        {text: 'Slide "Bin Size" to "week", then click anywhere outside the dropdown.', event: Events.ui.dropdown.hide},
      ]
      onFinish: ->
        Events.ui.nux.layerspanel2.trigger()
      ref: '.chart-container'
      top: 100
      left: 15
      arrowDir: 'left'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Going Back'
      msgs: 'Let us give the chart a title then add it to the dashboard.'
      instructions: [
        {text: 'Click the chart title and type in a new one, say "New Users Weekly".', event: Events.ui.title.add},
        {text: 'Click "Return to Dashboard"', event: Events.nav.dashbuilder.open},
      ]
      onFinish: ->
        Events.ui.nux.layerspanel3.trigger()
      ref: '.data-panel'
      top: 20
      left: 100
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .workspace-area, .workspace-title'
      title: 'Making Tables'
      msgs: 'We can also create a table using the same data.'
      instructions: [
        {text: 'Click the "Make Table" button', event: Events.ui.quickadd.expand},
        {text: 'Drag "signup_date" to "Columns"', event: Events.ui.metric.add},
        {text: 'Drag "count(*)" to "Columns"', event: Events.ui.metric.add},
        {text: 'Click "Draw Table"', event: Events.ui.pivottable.add},
      ]
      onFinish: ->
        Events.ui.nux.tablepanel.trigger()
      ref: '.workspace-area'
      top: 230
      left: 15
      arrowDir: 'leftlower'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Moving and Resizing'
      msgs: 'Great! This pivot table may be overlapping your chart, so let\'s drag it into a new position. Also, let\'s resize the pivot table by dragging the right bottom corner.'
      buttonText: 'Continue'
      onFinish: ->
        Events.ui.nux.workspace3.trigger()
      ref: '.data-panel'
      top: 70
      left: 25
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Edit Table'
      msgs: 'The table we created is actually a pivot table with many more features. Let\'s explore some pivot table options.'
      instructions: [
        {text: 'Move your mouse over the chart and click "Edit Table"', event: Events.nav.tablebuilder.open},
      ]
      onFinish: ->
        Events.ui.nux.workspace2.trigger()
      ref: '.data-panel'
      top: 70
      left: 25
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .chart-container'
      title: 'Table Builder'
      msgs: 'You can define additional columns or rows on the left, just like any other pivot table tool.'
      instructions: [
        {text: 'Drag "gender" to "Columns"', event: Events.ui.metric.add},
      ]
      onFinish: ->
        Events.ui.nux.tableedit.trigger()
      ref: '.chart-container'
      top: 50
      left: 15
      arrowDir: 'left'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Going Back'
      msgs: 'Now we see separate data for each gender.'
      instructions: [
        {text: 'Click "Return to Dashboard" when you are ready.', event: Events.nav.dashbuilder.open},
      ]
      onFinish: ->
        Events.ui.nux.tableedit2.trigger()
      ref: '.data-panel'
      top: 20
      left: 100
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .content-panel'
      template: 'tmpl-nux-data-panel'
      title: 'Deriving Columns'
      msgs: 'You can also create new columns to visualize. Let\'s use another data set to illustrate this.'
      instructions: [
        {text: 'Click on our second data set, "Sales Data"', event: Events.ui.table.open },
        {text: 'Click the "View/Edit" button beside our second data set, "Sales Data"', event: Events.nav.datatableviewer.open},
      ]
      onFinish: ->
        Events.ui.nux.datapanel2.trigger()
      ref: '.content-panel'
      top: 130
      left: 15
      arrowDir: 'leftlower'
    },
    {
      cover: 'HEADER, .chart-container'
      title: 'Deriving New Variables'
      msgs: 'We will now derive a new column called "profit" which is the difference of the columns "income" and "expense".'
      instructions: [
        {text: 'Type enter "profit" as the new column name, and "[income]-[expense]" as the formula, then click "Add Column"', event: Events.data.column.add },
      ]
      onFinish: ->
        Events.ui.nux.datanewcol.trigger()
      ref: '.chart-container'
      top: 70
      left: 15
      arrowDir: 'left'
    },
    {
      cover: 'HEADER, .data-panel, .menu-panel'
      title: 'Going Back'
      msgs: 'The new column should appear in the table. Let\'s go back and use it in a visualization!'
      instructions: [
        {text: 'Click "Go Back"', event: Events.nav.datatableviewer.close},
      ]
      onFinish: ->
        Events.ui.nux.workspace4.trigger()
      ref: '.data-panel'
      top: 20
      left: 100
      arrowDir: 'right'
    },
    {
      cover: 'HEADER, .workspace-area, .workspace-title'
      title: 'Making Numerals'
      msgs: 'Let\'s visualize the total sum of all profit as a single number.'
      instructions: [
        {text: 'Click the "Make Number" button', event: Events.ui.quickadd.expand},
        {text: 'Drag "profit" to "Value"', event: Events.ui.numeral.add},
      ]
      onFinish: ->
        Events.ui.nux.numeral.trigger()
      ref: '.workspace-area'
      top: 190
      left: 15
      arrowDir: 'leftlower'
    },
    {
      cover: '.data-panel, .menu-panel'
      title: 'Nicely Done!'
      msgs: [
        'You\'ve successfully created a chart, pivot table, and numeral. You have completed the tutorial.',
        'It\'s time to return to your data set by clicking "Home" above or by using your browser\'s back button.'

      ]
      buttonText: 'Finish'
      onFinish: =>
        Events.ui.nux.done.trigger()
        if not local
          serverApi.sendPost '/tutorial/mark-complete', {type: 'nux'}, (err) ->
            console.error err if err
      event: Events.nav.dashbuilder.open
      ref: '.data-panel'
      top: 20
      left: 25
    }
  ]

module.exports = tutorial
