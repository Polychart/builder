fs            = require('fs')
{spawn, exec} = require('child_process')
stitchTask    = require('./makeTools/stitchTask')
runServerTask = require('./makeTools/runServerTask')

EXPORT_SERVICE_PORT = 1342

module.exports = (grunt) ->
  grunt.initConfig
    pkg:         grunt.file.readJSON "package.json"
    tmpDir:      "tmp/build/"
    packageDir:  "polychartPackaged/"

    #### Multitask to compile source files with stitch.js
    stitch:
      main:
        dest: "compiledStatic/main/main.js"
        cwd: "src/"
        src:  [ "poly.coffee"
                "poly/*.coffee"
                "poly/demoData/*.js"
                "poly/common/*.coffee"
                "poly/examples/*.coffee"
                "poly/main/**/*.coffee"
                "poly/main/templates.js" ]

    #### Task to compile less files
    less:
      dependencies:
        files:
          "lib/jqueryui/jquery.ui.polychart.css": "lib/jqueryui/jquery.ui.polychart.less"

      main:
        files: [
          { src: [ "src/poly/main/polychart.less", "src/poly/home.less" ]
          , dest: "compiledStatic/main/main.css" }
          { src: "src/poly/common/oldLayout.less"
          , dest: "compiledStatic/common/oldLayout.css" }
          { src: "src/poly/common/goldilocks.css"
          , dest: "compiledStatic/common/goldilocks.css" }
        ]

    #### Task to concatenate files
    concat:
      options:
        separator: ";\n\n"
      dependencies:
        files: [
          { src: [ 'lib/cookies.js'
                   'lib/jquery-1.7.1.js'
                   'lib/jquery-toast/javascript/jquery.toastmessage.js'
                   'lib/jquery.caret.js'
                   'lib/jquery.event.drag-2.0.js'
                   'lib/jquery.simple-color.js'
                   'lib/jqueryui/jquery-ui-1.10.3.custom.min.js'
                   'lib/jqueryui/jquery.ui.touch-punch.min.js'
                   'lib/knockout.js'
                   'lib/moment.js'
                   'lib/underscore.js'
                   'lib/polychart2.js'
                   'lib/raphael.js'
                   'lib/shjs/sh_javascript.js'
                   'lib/shjs/sh_main.js'
                   'lib/slickgrid/slick.core.js'
                   'lib/slickgrid/slick.grid.js']
          , dest: "compiledStatic/common/dependencies.js" }
          { src: ['lib/jqueryui/jquery.ui.polychart.css'
                  'lib/shjs/sh_style.css'
                  'lib/slickgrid/slick.grid.polychart.css']
          , dest: 'compiledStatic/common/dependencies.css' }
        ]

    #### Task to watch coffee files
    watch:
      templates:
        files: ['src/**/*.tmpl']
        tasks: ['koTemplates', 'copy:mainTmp', 'stitch:main']
      mainScripts:
        files: [ 'src/poly/*.coffee'
                 'src/poly/common/*.coffee'
                 'src/poly/main/**/*.coffee'
                 'src/poly/main/**/*.js' ]
        tasks: ['copy:mainTmp', 'stitch:main']
      appStyles:
        files: [ 'src/poly/app.less'
                 'src/poly/home.less'
                 'src/poly/main/**/*.less' ]
        tasks: ['less:main']

    #### Tasks to copy files
    copy:
      mainTmp:
        files: [
          { expand: true
          , cwd: "<%= stitch.main.cwd %>"
          , src: "<%= stitch.main.src %>"
          , dest: "<%= tmpDir %>main_pkg/" }
        ]
      commonAssets:
        files: [
          { expand: true
          , cwd: "images/common"
          , src: ["**"]
          , dest: "compiledStatic/common/images" }
          { expand: true
          , cwd: "lib/sourcesanspro/TTF"
          , src: "*.ttf"
          , dest: "compiledStatic/common/fonts" }
        ]
      mainAssets:
        files: [
          { expand: true
          , cwd: "images/main"
          , src: ["**"]
          , dest: "compiledStatic/main/images" }
        ]
      package:
        files: [
          { expand: true
          , cwd: 'compiledStatic/common'
          , src: [ "**" ]
          , dest: "<%= packageDir %>/static" }
          { expand: true
          , cwd: 'compiledStatic/main'
          , src: [ "**" ]
          , dest: "<%= packageDir %>/static" }
          { expand: true
          , cwd: 'server'
          , src: [ "polychartQuery/**/*.py"
                 , "!polychartQuery/connections.py" ]
          , dest: "<%= packageDir %>" }
          { expand: true
          , cwd: 'packageExamples'
          , src: ["**"]
          , dest: "<%= packageDir %>" }
          { expand: true
          , cwd: "packageData"
          , src: ["**"]
          , dest: "<%= packageDir %>data/" }
        ]
      onprem:
        files: [
          { expand: true
          , cwd: "deployTools"
          , src: [ "install.py" ]
          , dest: "onprem" }
          { expand: true
          , src: [ "manage.py", "requirements", "system_requirements" ]
          , dest: "onprem" }
          { expand: true
          , cwd: "compiledStatic"
          , src: [ "**" ]
          , dest: "onprem/static" }
          { expand: true
          , cwd: "server"
          , src: [ "**" ]
          , dest: "onprem/server" }
        ]

    #### Task to clean destination dir
    clean: [
      "<%= packageDir %>"
      "<%= tmpDir %>"
      "compiledStatic/"
      "server/**/*.pyc"
      "onprem"
      "tmp/"
      "polychart-onprem-*.zip"
    ]

    #### Task to replace text found in files
    replace: {
      packageJS: {
        src: ['<%= packageDir %>/static/dependencies.js'
            , '<%= packageDir %>/static/main.js']
        overwrite: true,
        replacements: [{
          from: "/static/main/"
          to: "static/"
        }, {
          from: "/static/common/"
          to: "static/"
        }]
      }
      packageCSS: {
        src: ['<%= packageDir %>/static/dependencies.css'
            , '<%= packageDir %>/static/main.css' ]
        overwrite: true,
        replacements: [{
          from: "/static/main/"
          to: ""
        }, {
          from: "/static/common/"
          to: ""
        }]
      }
    }

  #### Load third party tasks
  grunt.loadNpmTasks 'grunt-contrib-clean'
  grunt.loadNpmTasks 'grunt-contrib-concat'
  grunt.loadNpmTasks 'grunt-contrib-copy'
  grunt.loadNpmTasks 'grunt-contrib-less'
  grunt.loadNpmTasks 'grunt-contrib-watch'
  grunt.loadNpmTasks 'grunt-text-replace'

  #### Define tasks
  grunt.registerTask 'default', [
    'clean'
    'build'
    'runServer'
    'watch'
  ]

  grunt.registerTask 'withExport', [
    'clean'
    'build'
    'runServer'
    'exportServer'
    'watch'
  ]

  grunt.registerTask 'onprem', [
    'clean'
    'build'
    'copy:onprem'
    'setOnpremFilePermissions'
    'writeOnpremVersion'
    'zipOnprem'
  ]

  grunt.registerTask 'package', [
    'clean'
    'build'
    'copy:package'
    'replace:packageJS'
    'replace:packageCSS'
    'docs'
  ]

  grunt.registerTask 'build', "General task to build", (target) ->
    target or= 'default'
    switch target
      when 'default'
        grunt.task.run [
          'copy:mainTmp'
          'copy:commonAssets'
          'copy:mainAssets'
          'koTemplates'
          'stitch:main'
          'less:dependencies'
          'less:main'
          'concat:dependencies'
        ]

  grunt.registerTask 'exportServer', "Run the Node.js server for exporting", () ->
    done = @async()
    server = spawn("coffee", ["exportService/server.coffee",  EXPORT_SERVICE_PORT])
    server.stdout.on 'data', (data) ->
      grunt.log.writeln data
    server.stderr.on 'data', (data) ->
      grunt.log.writeln "[Log]: #{data}"
    server.on 'close', (code) ->
      grunt.log.writeln "Export service has exited with code #{code}."
    done(true)

  grunt.registerTask 'koTemplates', "Compile Knockout-js templates", () ->
    done = @async()

    cmd = "makeTools/parseTemplates.py --source=src/ --dest=tmp/build/main_pkg/poly/main/templates.js"
    exec cmd, (err, stdout, stderr) ->
      if err
        done false
        throw err

      done true

  grunt.registerTask 'docs', "Compile Markdown documents to HTML", () ->
    done = @async()

    # Compile OEM docs
    cmd = "pandoc -f markdown -t html5 docs/oem.md > polychartPackaged/README.html"
    exec cmd, (err, stdout, stderr) ->
      if err
        done false
        throw err

      done true

  grunt.registerTask 'writeOnpremVersion', "Write a version file for the onprem package", () ->
    done = @async()

    cmd = "git describe"
    exec cmd, (err, stdout, stderr) ->
      if err
        done false
        throw err

      version = stdout.trim()
      fs.writeFile 'onprem/version', version, (err) ->
        if err
          done false
          throw err

        done true

  grunt.registerTask 'writeOnpremVersion', "Write a version file for the onprem package", () ->
    done = @async()

    getSoftwareVersion (err, version) ->
      if err
        done false
        throw err

      fs.writeFile 'onprem/version', version, (err) ->
        if err
          done false
          throw err

        done true

  grunt.registerTask 'setOnpremFilePermissions', "Fix the file permissions in the onprem package", () ->
    fs.chmodSync "onprem/install.py", 0o755
    fs.chmodSync "onprem/manage.py", 0o755

  grunt.registerTask 'zipOnprem', "Produce a zip file containing the onprem solution", () ->
    done = @async()

    getSoftwareVersion (err, version) ->
      if err
        done false
        throw err

      exec "zip -r ../polychart-onprem-#{version}.zip *", {cwd: 'onprem'}, (err) ->
        if err
          done false
          throw err

        done true

  getSoftwareVersion = (callback) ->
    exec "git describe", (err, stdout, stderr) ->
      if err
        callback err
        return

      callback null, stdout.trim()

  stitchTask.register grunt
  runServerTask.register grunt
