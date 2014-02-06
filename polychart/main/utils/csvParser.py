"""
Authors: Jeeyoung Kim, Luc Ritchie
Code to parse CSV files from the user.
"""
import csv
import re

from itertools import chain, ifilter, islice, izip, izip_longest

def parseForPreview(stream, format):
  """
  Parses the CSV file and formats it for previewing via Slickgrid
  """
  rows, header = parse(stream, format)

  # Translate from [['foo', 'bar', 'baz'], ['ping', 'pong', 'pang']] into
  # [
  #   {'col1': 'foo',  'col2': 'bar',  'col3': 'baz'},
  #   {'col1': 'ping', 'col2': 'pong', 'col3': 'pang'}
  # ]
  rows = [{x: y for (x, y) in zip(header, row)} for row in rows[0:100]]

  return {
    'status': 'success',
    'rows'  : rows,
    'header': header
  }

def parseForPolychart(stream, format):
  """
  Parses the CSV file and formats it for PolychartJS
  """
  rows, header = parse(stream, format)

  # Translate from [['foo', 'bar', 'baz'], ['ping', 'pong', 'pang']] into
  # {
  #   'col1': ['foo', 'ping'],
  #   'col2': ['bar', 'pong'],
  #   'col3': ['baz', 'pang']
  # }
  cols = zip(*rows) #transpose
  data = {y: cols[x] for x, y in enumerate(header)}

  # Translate header from ['col1', 'col2', 'col3'] into
  # {
  #   'col1': {type: 'cat'},
  #   'col2': {type: 'cat'},
  #   'col3': {type: 'cat'}
  # }
  header = {x: {'type': y} for (x, y) in izip(header, format['types'])}

  return {
    'name': format['tableName'],
    'data': data,
    'meta': header
  }

def unicodeCsvReader(csvReader):
  """
  Generator - wraps a CSV reader object to decode all cells using UTF-8
  """
  for row in csvReader:
    yield [unicode(cell, 'utf-8', 'ignore') for cell in row]

def parse(stream, format):
  """
  Parses the CSV file coming from the given stream.
  Returns a tuple of 2 lists: rows, header
  stream - input stream.
  """

  def getFormatArg(argName, defVal):
    return format[argName] if argName in format else defVal
  delimiter   = getFormatArg('delimiter',   ',')
  hasHeader   = getFormatArg('hasHeader',   True)
  rowsToKeep  = getFormatArg('rowsToKeep',  None)
  columnNames = getFormatArg('columnNames', None) or []

  raw_reader = csv.reader(stream, delimiter=str(delimiter))
  reader = unicodeCsvReader(raw_reader)

  # If no header is present, prepend an empty header which we'll fill in later
  if not hasHeader:
    reader = chain([[]], reader)

  # Slice off only as many rows as needed
  if rowsToKeep:
    # Add one to keep the first row as a header
    rows = islice(reader, int(rowsToKeep) + 1)
  else:
    rows = reader

  # Widen all rows to be as long as the longest one
  # This uses izip(*) magic to transpose
  # It also ensures that rows is a generator, which simplifies taking the header
  cols = izip_longest(*rows, fillvalue='')
  rows = izip(*cols)

  header = []
  for i, name in enumerate(rows.next()):
    if i < len(columnNames):
      name = columnNames[i] or name
    if name:
      header.append(name)
    else:
      header.append('Column_%s' % (i + 1))

  # Remove blank rows
  rows = ifilter(any, rows)

  return list(rows), header
