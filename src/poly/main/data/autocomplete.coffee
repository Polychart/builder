###
Lisa's Note:

This is mostly Jee's code that came from ggviz
It is an extension over JQuery UI Autocomplete that:
 - allows multiple items to be selected 
 - with other text between them
 - place square brackets around each selected item
Essentially, the selected items are column names, and the autocomplete is
used to assist users in typing in formulas to derive new columns based on
the existing ones.
###

_replace = (string) ->
  # note: this is NOT an escaping function
  # rather, it replaces escaped version of "[" and "]" with something else so
  # they do not interfere with finding the last REAL "["
  string.replace(/\\\]/g,'@@').replace(/\\\[/g,'@@')

# from chartbuilder/src/coffee/metric_name.coffee
findLastBegin = (string, _char, startIndex) ->
  string = _replace string
  index = startIndex
  while index > -1
    if (string.charAt(index) == _char)
      return index
    else
      index--
  return -1
findEnd = (string, startIndex) ->
  index = startIndex
  string = _replace string
  while index < string.length
    if string.charAt(index) == ']'
      return index
    else
      index++
  return -1

extractLast = (string, selectionStart, selectionEnd) ->
  if selectionStart != selectionEnd
    return null
  start = findLastBegin(string, '[', selectionStart)
  temp =  findLastBegin(string, ']', selectionStart)
  if temp > start and (temp != selectionStart and temp != string.length - 1)
    return null
  # this needs to be modified.
  # end = string.indexOf(']', start)
  end = findEnd(string, start)
  if start > -1
    if end == -1
      return [start+1, string.length]
    else
      return [start+1, end]
  return null

autocompleteSelect = (event, ui) ->
  # this = jquery autocomplete.
  oldValue = @value
  {selectionStart, selectionEnd} = this
  range = extractLast(oldValue, selectionStart, selectionEnd)
  if range is null
    # don't do anything if range is null, but this shouldn't be hit.
    return
  beginning = oldValue.substring(0, range[0])
  end = oldValue.substring(range[1])
  originalValue = ui.item.value
  replacedValue = originalValue
  value = replacedValue
  if not (end.length > 0 and end.charAt(0) == ']')
    value += ']'
  newValue = beginning + value + end
  @value = newValue
  cursorLocation = beginning.length + replacedValue.length + 1
  return cursorLocation


module.exports = { findLastBegin, findEnd, extractLast, autocompleteSelect, unescape}
