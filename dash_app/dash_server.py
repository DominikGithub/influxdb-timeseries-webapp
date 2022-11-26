#! /usr/bin/env python3

"""
Dash/plotly based web data visualization app.
"""

import os
import flask
import arrow
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import dash_auth
from dash import dcc
from dash import Dash, dash_table, dcc, html
from dash.dependencies import State, Input, Output
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

server = flask.Flask(__name__)
app = Dash(server=server, suppress_callback_exceptions=True)
app.title = 'Dash web app'

# get ui secrets
auth = dash_auth.BasicAuth(app, {os.environ['ui_user']:os.environ['ui_password']} )

# influxdb
INFLUXDB_URL = "http://influxdb:8086"
# INFLUXDB_URL="http://localhost:8086"
INFLUXDB_BUCKET_STOCKS = os.environ['INFLUXDB_BUCKET_STOCKS']
INFLUXDB_ORG = os.environ['INFLUXDB_ORG']
INFLUXDB_TOKEN = os.environ['INFLUXDB_API_TOKEN']

def influxdb_get_df(flux_client, flux_query, org):
    """
    NOTE replacement for buggy: client.query_api().query_data_frame(query, org=INFLUXDB_ORG)
    """
    httpResp = flux_client.query_api().query_raw(flux_query, org=org)
    # skip http header lines
    __ign_header = [httpResp.readline() for _ in range(3)]
    try:
        df = pd.read_csv(httpResp, on_bad_lines='skip')
        df = df[df['result'].isna()]
        df = df.drop(columns=df.columns[:3])
    except pd.errors.EmptyDataError:
        df = pd.DataFrame()
    except Exception as ex:
        raise ex
    return df


@app.callback(
    Output('influxdb-data-container', 'children'),
    [Input('id-influxdb-symbol-dropdown', 'value'),
     Input('id-influxdb-metric-dropdown', 'value'),
     Input(component_id='influxdb-stocks-date-picker', component_property='start_date'),
     Input(component_id='influxdb-stocks-date-picker', component_property='end_date')]
)
def get_influxdb__faultcode_table(symbol, metric, start_date, end_date):
    """
    Get stock metric from Influxdb to be shown as a table.
    """
    pyar_ts_start = arrow.get(start_date)
    pyar_ts_stop = arrow.get(end_date)
    
    flux_query = f'''from(bucket: "{INFLUXDB_BUCKET_STOCKS}") 
                        |> range(start: -6mo)
                        //|> filter(fn: (r) => r.symbol == "{symbol}" and r._field == "{metric.lower()}")
                        |> filter(fn: (r) => r.symbol == "{symbol}")
                        |> filter(fn: (r) => r._time >= time(v: "{pyar_ts_start.format('YYYY-MM-DD')}T00:00:00.000Z") and r._time <= time(v: "{pyar_ts_stop.format('YYYY-MM-DD')}T23:59:59.000Z") )
                        |> keep(columns: ["_time", "_field", "_value", "symbol"])'''
    try:
        flux_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
        df = influxdb_get_df(flux_client, flux_query, INFLUXDB_ORG)

        # if empty
        if df.shape[0] <= 0: return html.Plaintext(['No data available'])
        df = df.sort_values(by=['_time'], ascending=False)
        print(df)

        ###### plots
        graph_lst = []

        # table
        dft = df.pivot(index='_time', columns='_field', values=['_value'])

        dft['date'] = dft.index
        dft.columns = dft.columns.get_level_values(1)
        print(dft)

        ft = go.Figure(data=[
            go.Table(
                header=dict(
                    values=dft.columns,
                    font=dict(size=12),
                    align="left"
                ),
                cells=dict(
                    values=[dft[k].tolist() for k in dft.columns], # [1:]
                    align="left")
            )
        ])
        graph_lst.append(dcc.Graph(figure=ft, style={'flex-grow':'2', 'align-items':'flex-start'}))


        # volume
        metric_name = 'volume'
        mdf = df[df['_field'] == metric_name]
        fv = go.Figure(data=[
            go.Scatter(x=mdf['_time'], y=mdf['_value'],
                        mode='lines',
                        showlegend=True,
                        text=mdf['_field'],
                        name=metric_name)
        ])
        graph_lst.append(dcc.Graph(figure=fv, style={'flex-grow':'2', 'align-items':'flex-start'}))

        # open, low, high, close
        fig = go.Figure()
        for metric_name in df['_field'].unique():
            if metric_name == 'volume': continue
            print(metric_name)

            mdf = df[df['_field'] == metric_name]
            fig.add_trace(go.Scatter(x=mdf['_time'], y=mdf['_value'],
                        mode='lines',
                        showlegend=True,
                        name=metric_name))
        graph_lst.append(dcc.Graph(figure=fig, style={'flex-grow':'2', 'align-items':'flex-start'}))

        return html.Div([
                html.Div([dash_table.DataTable(df.to_dict('records'))], style={'flex-grow':'1'}),
                html.Div(graph_lst, style={'flex-grow':'2', 'align-items':'flex-start'}),
        ], style={'display':'flex', 'flex-direction':'row', 'justify-content':'space-evenly', 'align-items':'flex-start'})
    finally:
        flux_client.close()


app.layout = html.Div([
    html.Div([
      html.Plaintext(['Data web app']),
      html.Div([
            html.Div([
                dcc.Dropdown(['IBM'], 'IBM',                                      # TODO load from db
                                    id='id-influxdb-symbol-dropdown', 
                                    clearable=False,
                                    style={'width':'300px', 'marginLeft':'0%'}),
                dcc.Dropdown(['Open','Low','High','Close','Volume'], 'Open', 
                                    id='id-influxdb-metric-dropdown', 
                                    clearable=False,
                                    style={'width':'200px', 'marginLeft':'0%'}),
                dcc.DatePickerRange(
                    id='influxdb-stocks-date-picker',
                    display_format='YYYY-MM-DD',
                    min_date_allowed = date.today() - relativedelta(months=6),
                    max_date_allowed = date.today(),
                    start_date = date.today() - timedelta(days=1), 
                    end_date = date.today() 
                ),
                # dcc.LogoutButton(),       # NOTE not recommended to use anymore!
                ], style={'display':'flex', 'alignItems':'center', 'columnGap':'1%', 'marginTop':'2px'}),
                dcc.Loading(
                        id="loading-influxdb-stocks-table",
                        type="circle",
                        children=html.Div(id="influxdb-data-container")
                )
          ])
    ])
])


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=8080)
