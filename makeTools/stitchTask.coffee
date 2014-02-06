fs = require 'fs'
path = require 'path'
stitch = require 'stitch'

# Creates a directory and all missing parent directories
createDirectory = (dirPath) ->
  if fs.statSync(path.dirname(dirPath)).isDirectory()
    return

  parentDirPath = path.dirname path
  if parentDirPath isnt dirPath
    createDirectory parentDirPath

  fs.mkdirSync dirPath

module.exports.register = (grunt) ->
  grunt.registerMultiTask 'stitch', "Build and stitch files together", () ->
    done = @async()

    config = @files[0]
    pkg = stitch.createPackage(paths: ["#{grunt.config('tmpDir')}#{@target}_pkg"])
    pkg.compile (err, src) ->
      if err
        done(false)
        console.log err
        throw err

      try
        createDirectory path.dirname config.dest
        fs.writeFile config.dest, src, (err) ->
          if err? then throw err
          done(true)
      catch err
        console.error err
        done(false)
