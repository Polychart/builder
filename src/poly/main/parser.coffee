###
# Module containing utilities to extract information from Polychart2.js names
#
# NOTE: Most of these are included for backwards compatibility
#       The information here should be encoded in the builder specs
###

class Parser
  #### Rudimentary parser to extract names, binwidths, statistics by means of RegExp
  getName: (spec) ->
    if spec.name?
      return spec.name
    if spec.var == 'count(1)'
      return 'count(*)'
    # for backwards compatibility:
    match = /(^count\(\*\)$)|^bin\((.*),.*\)|^(?:count|mean|unique|sum)\((.*)\)$/.exec(spec.var)
    fullName = if match? then _.compact(match)[1] else spec.var
    tableNameReg      = new RegExp "(.*?)\\.(.*)"
    match = tableNameReg.exec(fullName)
    if match?
      match[2]
    else
      fullName

  getTableName: (name) =>
    #### Obtain the table name using just the string
    if not _.isString(name)
      name = @getName(name)
    tableNameReg      = new RegExp "(.*?)\\.(.*)"
    match = tableNameReg.exec(name)
    if match?
      match[1]
    else
      null

  getBinwidth: (spec) ->
    if spec.bin?
      return spec.bin
    # for backwards compatibility:
    match = /(?:bin\()[^,]*,(\w*)\)/.exec(spec.var)
    if match? then match[1] else null

  getStats: (spec) ->
    if spec.stat?
      return spec.stat
    name = spec.var
    if name == 'count(1)'
      return null
    # for backwards compatibility:
    match = /^count\(\*\)|$|(bin|count|mean|unique|sum)(?:\(.*\)$)/.exec(name)
    if match? then match[1] else null

module.exports = new Parser()
