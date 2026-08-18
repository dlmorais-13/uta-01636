"""
File with utility functions for date operations.
"""

from datetime import datetime as dt
import pytz

TZ = pytz.timezone("America/Denver")

def Agol_Now():
  """
  Returns the current date formatted the way it is expected
  by ArcGIS Online in Feature editing operations.

  Returns:
    The current date as expected by ArcGIS Online.
  """
  return TZ.localize(dt.now()).isoformat(timespec="seconds")
