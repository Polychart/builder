{spawn, exec} = require('child_process')

module.exports.register = (grunt) ->
  grunt.registerTask 'runServer', "Run local Django development server.", () ->
    done = @async()
    exec "./manage.py syncdb --migrate -v 0", (err) ->
      if err?
        done(false)
        console.log err
        throw err
      server = spawn("./manage.py", ["runserver", "--nothreading"])
      done(true)

      server.stdout.on 'data', (data) ->
        grunt.log.writeln data
      server.stderr.on 'data', (data) ->
        grunt.log.writeln "[Log]: #{data}"
      server.on 'close', (code) ->
        grunt.log.writeln "Server exited with code #{code}."
