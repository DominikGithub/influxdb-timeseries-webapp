#! /usr/bin/env python3

"""
Frequently scrape timeseries stock data and write to Influxdb.
"""

import pandas as pd
import requests
import os
from influxdb_client import InfluxDBClient, Point, WriteOptions
from influxdb_client.client.write_api import SYNCHRONOUS
try:
	from dotenv import load_dotenv
	load_dotenv()
except: pass

av_url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize=full&apikey={token}"
AV_API_TOKEN = os.environ['ALPHAVANTAGE_API_TOKEN']

INFLUXDB_ORG = os.environ['INFLUXDB_ORG']
INFLUXDB_API_TOKEN = os.environ['INFLUXDB_API_TOKEN']
INFLUXDB_BUCKET_STOCKS = os.environ['INFLUXDB_BUCKET_STOCKS']


def load_data(comp_smybol="IBM", freq="1min"):
	"""
	Load stock data from rest API.
	"""
	r = requests.get(av_url.format(symbol=comp_smybol, interval=freq, token=AV_API_TOKEN))
	pyld = r.json()

	print('keys', pyld.keys())
	print('Meta Data', pyld['Meta Data'])

	ser_key = f"Time Series ({freq})"
	ser = pyld[ser_key]

	df = pd.DataFrame(ser).transpose()
	df = df.rename(lambda c: c.split(" ")[1], axis='columns')
	return df


def write_to_influxdb(df, symbol="IBM", metric="open"):
	"""
	Write data into timeseries db.
	"""
	with InfluxDBClient(url="http://influxdb:8086", token=INFLUXDB_API_TOKEN, org=INFLUXDB_ORG) as _client:
		with _client.write_api(write_options=WriteOptions(batch_size=100,
															flush_interval=2_000,
															jitter_interval=2_000,
															retry_interval=5_000,
															max_retries=5,
															max_retry_delay=30_000,
															exponential_base=2)) as _write_client:

			for ts, row in df.iterrows():
				timestamp = 'T'.join(ts.split(" "))
				print(symbol, timestamp, metric, row[metric])
				point = Point("stock") \
							.field(metric, float(row[metric])) \
							.tag("symbol", symbol) \
							.time(timestamp+'.000000000Z')
				_write_client.write(bucket=INFLUXDB_BUCKET_STOCKS, record=point)


if __name__ == "__main__":
	comp_smybol = 'IBM'
	# get stock data
	df = load_data(comp_smybol)
	print(df)
	
	# write data to influxdb
	for metric in df.columns:
		print("writing", metric)
		write_to_influxdb(df, symbol=comp_smybol, metric=metric)

