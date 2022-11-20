# tools-influxdb-dash

Collect historical stock data from Alphavanteage API and store into Influxdb timeseries db.  


### Setup & run  
Set `.env` file credentials  
* alphavantage_scraper/.env
* influxdb/.env  
```
$ docker-compose up --build --detach  
```

NOTE: temp fix for initial access token missing.  
1) Start Influxdb: Create all access API tocken > set in scraper dir `.env`  
2) Restart scraper script  


## Influxdb  
Timerseries database 2.5.1  
Web interface `<HOST URL>:8086/`  

## Python scraper  
Collecting time series data from REST API  

