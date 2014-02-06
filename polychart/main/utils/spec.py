"""
Functions related to processing frontend spec objects.
"""
import re


def getDsInfo(spec):
  """
  Extracts the list of (tableName, dsKey) pairs from the clientside chart
  specification produced by the Dashboard Builder.

  Args:
    spec: A dictionary corresponding to the client side chart spec object. The
      spec object must have the field 'meta', whose value will be a dictionary
      with keys as column names and values as dictionaries that contain the
      desired information. For example:

        spec = { ...
                 meta: { columnOne: { tableName: "Table_One", dsKey: "keyone" , ... }
                       , columnTwo: { tableName: "Table_Two", dsKey: "keyone" , ...}
                       ... }
                ... }

  Returns:
    A list of distinct pairs with tableName in the first entry and dsKey in the
    second. Both values will be strings.
  """
  result = []
  for _, val in spec['meta'].iteritems():
    pair = (val.get('tableName'), val.get('dsKey'))
    if pair[0] is None and pair[1] is None:
      continue
    elif pair not in result:
      result.append(pair)
  return result
