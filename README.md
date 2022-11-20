# tools-influxdb-dash

Collect historical stock data from Alphavanteage API and store into Influxdb timeseries db.  


### Setup & run  
Set `.env` file credentials  
* alphavantage_scraper/.env
* influxdb/.env  
* dash_app/.env  
```
$ docker-compose up --build --detach  
```

NOTE: temp fix for initial access token missing.  
1) Start Influxdb: Create all access API tocken > set in scraper dir `.env`  
2) Restart scraper script  


## Influxdb  
Timerseries database 2.5.1  
Web interface `<HOST URL>:8086/`  
![influxdb notebook](/res/20221120_influxdb.PNG)


## Python scraper  
Collecting time series data from REST API  

## Dash web app  
Web interface for data visualization  
Web interface `<HOST URL>:8080/`  

![dash app](/res/20221120_dash_app.PNG)

### Debug  
Show dash server logs:  
```
$ docker ps  
$ docker logs -f 1e3  
```
