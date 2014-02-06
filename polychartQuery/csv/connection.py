"""
Module defining a dummy CSV connection.
"""
from polychartQuery.abstract import DataSourceConnection

class Conn(DataSourceConnection):
  """
  Dummy class (for now)
  """
  def __init__(self, *args, **kwargs):
    super(Conn, self).__init__(*args, **kwargs)
    pass
