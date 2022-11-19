#! /usr/bin/env python3

"""
Frequently scrape timeseries stock data and write to Influxdb.
"""

import requests
import os
try:
  from dotenv import load_dotenv
  load_dotenv()
except: pass

AV_API_TOKEN = os.environ['ALPHAVANTAGE_API_TOKEN']


def scrape():
  """
  Load data from API.
  """
  url = f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY&symbol=IBM&apikey={AV_API_TOKEN}'
  r = requests.get(url)
  data = r.json()
  print(data)


if __name__ == "__main__":
  scrape()