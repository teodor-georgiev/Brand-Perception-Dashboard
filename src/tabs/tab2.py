import pandas as pd
from PIL import Image
from dash import dcc, html, Input, Output, State
import dash_daq as daq
import plotly.express as px
import dash_bootstrap_components as dbc
from utils.styles import *
import plotly.graph_objects as go
from utils.functions import *
import numpy as np
from plotly.subplots import make_subplots
from dash import callback
import os
import datetime
import base64
import io
import csv

# Tab 2
# Read the data
df_stocks_days = pd.read_csv("data/tab2/aggregated_stocks_values_days.csv")
df_stocks_weeks = pd.read_csv("data/tab2/aggregated_stocks_values_weeks.csv")
brands_list = df_stocks_days["Brand Name"].unique()

# remove AirBnb and Pepsi from numpy array
brands_list = brands_list[np.where((brands_list != "Airbnb") & (brands_list != "Pepsi"))]


if os.path.isfile("data/tab2/new_stocks/Stocks_daily.csv"):
    df_stocks_days = concatenate_df(df_stocks_days, "data/tab2/new_stocks/Stocks_daily.csv","Brand Name")
if os.path.isfile("data/tab2/new_stocks/Stocks_weekly.csv"):
    df_stocks_weeks = concatenate_df(df_stocks_weeks, "data/tab2/new_stocks/Stocks_weekly.csv","Brand Name")
    
# Twitter Sentiment
df_sentiment_overall = pd.read_csv("data/tab2/twitter_sentiment_overall.csv")

df_tweets_sentiment_daily = pd.read_csv("data/tab2/twitter_sentiment_daily_percent.csv")
df_tweets_sentiment_weekly = pd.read_csv("data/tab2/twitter_sentiment_weekly_percent.csv")
df_tweets_sentiment_monthly = pd.read_csv("data/tab2/twitter_sentiment_monthly_percent.csv")

# Twitter Count
df_tweets_count_daily = pd.read_csv("data/tab2/twitter_count_daily.csv")
df_tweets_count_weekly = pd.read_csv("data/tab2/twitter_count_weekly.csv")

if os.path.isfile("data/tab2/new_tweets/twitter_sentiment_day_percent.csv"):
    df_tweets_sentiment_daily = concatenate_df(df_tweets_sentiment_daily, "data/tab2/new_tweets/twitter_sentiment_day_percent.csv","brand")
    df_tweets_sentiment_weekly = concatenate_df(df_tweets_sentiment_weekly, "data/tab2/new_tweets/twitter_sentiment_week_percent.csv","brand")
    df_tweets_sentiment_monthly = concatenate_df(df_tweets_sentiment_monthly, "data/tab2/new_tweets/twitter_sentiment_month_percent.csv","brand")
    df_tweets_count_daily = concatenate_df(df_tweets_count_daily, "data/tab2/new_tweets/twitter_count_daily.csv","brand")
    df_tweets_count_weekly = concatenate_df(df_tweets_count_weekly, "data/tab2/new_tweets/twitter_count_weekly.csv","brand")

# Stocktwits Sentiment
df_stocktwits_daily = pd.read_csv("data/tab2/stocktwits_daily.csv")
df_stocktwits_weekly = pd.read_csv("data/tab2/stocktwits_weekly.csv")
df_stocktwits_monthly = pd.read_csv("data/tab2/stocktwits_monthly.csv")
df_stocktwits_overall = pd.read_csv("data/tab2/stocktwits_overall.csv")





# Stocktwits Count
df_stocktwits_count_daily = pd.read_csv("data/tab2/stocktwits_daily_count.csv")
df_stocktwits_count_weekly = pd.read_csv("data/tab2/stocktwits_weekly_count.csv")

# Read the new data
if os.path.isfile("data/tab2/new_stocktwits/stocktwits_daily_count.csv"):
    df_stocktwits_daily = concatenate_df(df_stocktwits_daily, "data/tab2/new_stocktwits/stocktwits_daily.csv","brand")
    df_stocktwits_weekly = concatenate_df(df_stocktwits_weekly, "data/tab2/new_stocktwits/stocktwits_weekly.csv","brand")
    df_stocktwits_monthly = concatenate_df(df_stocktwits_monthly, "data/tab2/new_stocktwits/stocktwits_monthly.csv","brand")
    df_stocktwits_count_daily = concatenate_df(df_stocktwits_count_daily, "data/tab2/new_stocktwits/stocktwits_daily_count.csv","brand")
    df_stocktwits_count_weekly = concatenate_df(df_stocktwits_count_weekly, "data/tab2/new_stocktwits/stocktwits_weekly_count.csv","brand")

# Daily
df_stocktwits_daily["polarity"] *= 100
df_stocktwits_daily["positive"] = (df_stocktwits_daily["polarity"] + 100) / 2
df_stocktwits_daily["negative"] = abs(df_stocktwits_daily["positive"] - 100)

# Weekly
# df_stocktwits_weekly["polarity"] *= 100
df_stocktwits_weekly["positive"] = (df_stocktwits_weekly["polarity"] + 100) / 2
df_stocktwits_weekly["negative"] = abs(df_stocktwits_weekly["positive"] - 100)

# Monthly
# df_stocktwits_monthly["polarity"] *= 100
df_stocktwits_monthly["positive"] = (df_stocktwits_monthly["polarity"] + 100) / 2
df_stocktwits_monthly["negative"] = abs(df_stocktwits_monthly["positive"] - 100)

# YouGov
df_yougov_daily = pd.read_csv("data/tab2/yougov_daily.csv")
df_yougov_weekly = pd.read_csv("data/tab2/yougov_weekly.csv")
df_yougov_monthly = pd.read_csv("data/tab2/yougov_monthly.csv")
df_yougov_overall = pd.read_csv("data/tab2/yougov_overall.csv")

df_yougov_monthly["Date"] = pd.to_datetime(df_yougov_monthly["Date"])
df_yougov_monthly["Date"] = df_yougov_monthly["Date"] + pd.offsets.MonthEnd()

if os.path.isfile("data/tab2/new_YouGov/yougov_daily.csv"):
    df_yougov_daily = concatenate_df(df_yougov_daily, "data/tab2/new_YouGov/yougov_daily.csv","Brand")
    df_yougov_weekly = concatenate_df(df_yougov_weekly, "data/tab2/new_YouGov/yougov_weekly.csv","Brand")
    df_yougov_monthly = concatenate_df(df_yougov_monthly, "data/tab2/new_YouGov/yougov_monthly.csv","Brand")
    

yougov_brand_presence = ["Awareness","Attention","WOM Exposure","Ad Awareness","Buzz"]
yougov_brand_image = ["Impression","Quality","Value","Recommend","Satisfaction","Reputation"]
yougov_brand_relationship = ["Consideration", "Purchase Intent", "Current Customer ", "Former Customer"]

brands_list = df_yougov_daily["Brand"].unique()
# Options for the dropdown menu in the monthly and radar YouGov charts
options = ['Image', 'Pressence', 'Relationship']
radar_options = [{'label': option, 'value': option} for option in options]
# Default wordcloud image for the first time the page is loaded
apple_wordcloud_img = Image.open("data/tab2/wordclouds/Apple_positive_wordcloud_square.png")


# Dictionary to map the charts to their names and corresponding column names in the dataframes
charts = {"Stock Price":"Close","Stock Price % Change" :"pct_change","Stock Volume":"Volume","Twitter Polarity":"polarity","Tweets Count" : "tweets_count",
          "Stocktwits Polarity":"polarity","Stocktwits Count":"stocktwits_count"}
yougov_charts = { col: col for col in df_yougov_daily.columns[1:-1]}
charts.update(yougov_charts)

# Dictionary to map the charts to their axis names
charts_axis_names = {"Stock Price":"Stock Price","Stock Price % Change" :"Stock Price % Change","Stock Volume":"Stock Volume","Twitter Polarity":"Twitter Polarity",
                     "Tweets Count" : "Tweets Count","Stocktwits Polarity":"Stocktwits Polarity","Stocktwits Count":"Stocktwits Count"}
charts_axis_names.update(yougov_charts)


dropdown_options_tab2_1 = list(charts.keys())
dropdown_options_tab2_2 = list(charts.keys())


UPLOAD_STYLE = {
                    'width': '100%',
                    'height': '30px',
                    'lineHeight': '30px',  # Reduce the lineHeight to match the height of the box
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                }
upload_field = dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files',id="upload-button")
                ], className='upload-area',style={"justify-content": "center","align-items": "center",'textAlign': 'center',"float":"left","margin-left":"50px"}),
                style=UPLOAD_STYLE,
                # Allow multiple files to be uploaded
                multiple=True
            )

# Begin Content of sidebar in Tab 2
switch_1_tab_2 =  html.Div(
            [
            html.P("Toggle Day/Week",style = SWITCH_NAME),
            daq.BooleanSwitch(id='day-week-switch',on=False,style = SWITCH)
            ]
            ,style ={"height":"40px"}
)

sidebar_2 = [
        html.H3("Filters", style={"textAlign": "center","margin-bottom":"1rem"}),
        html.Hr(style={"margin-top":"1px"}),
        html.Img(id="brand-image",src="assets/Apple.png",style={"width":"100%","height":"110px","object-fit":"contain","margin-top":"-30px"}),
        dbc.Nav
        (
            [
                html.Label('Select Brand'),
                dcc.Dropdown(brands_list, 'Apple', id='brand-dropdown',clearable=False),
                html.Br(),
                
                html.Label('Select Y-Axis'),
                dcc.Dropdown(dropdown_options_tab2_1,"Stock Price",id='chart-dropdown',clearable=False),
                html.Br(),
                
                html.Label('Select Additional Y-Axis'),
                dcc.Dropdown(dropdown_options_tab2_2,None,id='chart-dropdown-2',clearable=True),
                html.Br(),
                
                switch_1_tab_2,
                upload_field  
            ],
            vertical=True,
            pills=True,
            style={"margin-top": "10px"}
        ) 
]
# End of content of sidebar in Tab 2

# Begin content of main content in Tab 2

brand_stocks_chart = dcc.Graph(
    id='brand_stocks_chart',
    style={**BASE_CHART,
           "width": "1191px"
    },
    config=GRAPH_CONFIG
)

wordcloud_tabs = dcc.Tabs(
    id="tabs_wordcloud",
    value='positive',
    children=[
        dcc.Tab(
            label='Positive',
            value='positive',
            style={**SMALL_TABS, 'width':'50px'},
            selected_style={**SMALL_TABS_SELECTED, 'width':'50px'}
        ),
        dcc.Tab(
            label='Negative',
            value='negative',
            style={**SMALL_TABS, 'width':'50px'},
            selected_style={**SMALL_TABS_SELECTED, 'width':'50px'}
        )
    ],
    style={
        "position": "absolute",
        "top": "5px",
        "left": "210px",
        "font-size": "11px"
    }
)

wordcloud = html.Div(
    [
        html.P("Twitter Word Cloud", style=WORDCLOUD_LABEL),
        html.Img(
            id="wordcloud",
            src=apple_wordcloud_img,
            style={
                "object-fit": "contain",
                "width": "99%",
                "height": "90%",
                "margin-right": "5px"
            }
        ),
        wordcloud_tabs
    ],
    style=WORDCLOUD_PARENT
)

content_first_row = html.Div(
    [ 
        brand_stocks_chart,
        wordcloud
    ]
)
  

radar_dropdown = html.Div(
    dcc.Dropdown(
        id='radar-dropdown',
        options=radar_options,
        value='Image',
        clearable=False,
        style=YOUGOV_SMALL_DROPDOWN
    ),
    style=YOUGOV_SMALL_DROPDOWN_PARENT
)

yougov_monthly_dropdown = html.Div(
    dcc.Dropdown(
        id='yougov-monthly-dropdown',
        options=radar_options,
        value='Image',
        clearable=False,
        style=YOUGOV_SMALL_DROPDOWN
    ),
    style=YOUGOV_SMALL_DROPDOWN_PARENT
)


content_second_row = html.Div(
    [
        dcc.Graph(
            id="crosscorrelation_chart",
            style={
                **BASE_CHART,
                "width": "665px",
                "margin-left": "3px"
            },
            config=GRAPH_CONFIG
        ),
        html.Div(
            [
                yougov_monthly_dropdown,
                dcc.Graph(
                    id="yougov_monthly",
                    config=GRAPH_CONFIG
                ),
            ],
            style={
                **YOUGOV_CHART,
                "width": "786px"
            }
        ),
        html.Div(
            [
                radar_dropdown,
                dcc.Graph(
                    id="brand_overall_relationship",
                    style={},
                    config=GRAPH_CONFIG
                )
            ],
            style={
                **YOUGOV_CHART,
                "width": "385px"
            }
        ),
    ],
    style={"margin-left": "-338px"}
)

day_week_month_tabs =  [dcc.Tab(label='D', value='D',style=SMALL_TABS,selected_style=SMALL_TABS_SELECTED),
                        dcc.Tab(label='W', value='W',style=SMALL_TABS,selected_style=SMALL_TABS_SELECTED),
                        dcc.Tab(label='M', value='M',style=SMALL_TABS,selected_style=SMALL_TABS_SELECTED)]

content_third_row = html.Div(
    [
        dcc.Graph(
            id="brand_overall_sentiment",
            style={
                **BASE_CHART,
                "width": "300px",
                "margin-left": "3px",
                "margin-bottom": "10px"
            },
            config=GRAPH_CONFIG
        ),
        html.Div(
            [
                dcc.Graph(
                    id="brand_sentiment_time_chart",
                    style={
                        "border": "1px solid #e0e0e0",
                        "width": "100%",
                        "background-color": "white",
                        "border-radius": "10px"
                    },
                    config=GRAPH_CONFIG
                ),
                dcc.Tabs(
                    id="tabs_sentiment",
                    value="D",
                    children=day_week_month_tabs,
                    style={
                        "position": "absolute",
                        "top": "5px",
                        "left": "82%",
                        "font-size": "11px"
                    }
                ),
            ],
            style={
                "position": "relative",
                "width": "615px",
                "float": "left",
                "margin-top": "10px",
                "margin-left": "10px",
            }
        ),
        dcc.Graph(
            id="brand_overall_stocktwits_sentiment",
            style={
                **BASE_CHART,
                "width": "300px",
                "margin-left": "10px",
                "margin-bottom": "10px"
            },
            config=GRAPH_CONFIG
        ),
        html.Div(
            [
                dcc.Graph(
                    id="brand_sentiment_time_chart_StockTwits",
                    style={
                        "border": "1px solid #e0e0e0",
                        "width": "100%",
                        "background-color": "white",
                        "border-radius": "10px"
                    },
                    config=GRAPH_CONFIG
                ),
                dcc.Tabs(
                    id="tabs_sentiment_StockTwits",
                    value="W",
                    children=day_week_month_tabs[1:],
                    style={
                        "position": "absolute",
                        "top": "5px",
                        "left": "85%",
                        "font-size": "11px"
                    }
                ),
            ],
            style={
                "position": "relative",
                "width": "612px",
                "float": "left",
                "margin-top": "10px",
                "margin-left": "10px",
            }
        ),        
    ],
    style={"margin-left": "-338px"}
)

content_tab2 = [content_first_row, content_second_row, content_third_row]

# Callbacks for Tab 2
@callback(Output("brand_stocks_chart","figure"),
              Output("crosscorrelation_chart","figure"),
              Input("brand-dropdown","value"),
              Input("chart-dropdown","value"),
              Input("chart-dropdown-2","value"),
              Input("day-week-switch","on"),
              )
def update_brand_stocks_chart(brand_dropdown, chart_dropdown, chart_dropdown_2, day_week_switch):
    # Read the data depending on the day/week switch
    if day_week_switch:
        df_stocks_filtered = df_stocks_weeks[df_stocks_weeks["Brand Name"] == brand_dropdown]
        df_tweets_filtered = df_tweets_sentiment_weekly[df_tweets_sentiment_weekly["brand"] == brand_dropdown]
        df_tweets_count_filtered = df_tweets_count_weekly[df_tweets_count_weekly["brand"] == brand_dropdown]
        df_stocktwits_filtered = df_stocktwits_weekly[df_stocktwits_weekly["brand"] == brand_dropdown]
        df_stocktwits_count_filtered = df_stocktwits_count_weekly[df_stocktwits_count_weekly["brand"] == brand_dropdown]
        df_yougov_filtered = df_yougov_weekly[df_yougov_weekly["Brand"] == brand_dropdown]
        title_prefix = "Weekly "
        lag_periods, lag_step = 56, 7
        lag_name = "(Weeks)"
    else:    
        df_stocks_filtered = df_stocks_days[df_stocks_days["Brand Name"] == brand_dropdown]
        df_tweets_filtered = df_tweets_sentiment_daily[df_tweets_sentiment_daily["brand"] == brand_dropdown]
        df_tweets_count_filtered = df_tweets_count_daily[df_tweets_count_daily["brand"] == brand_dropdown]
        df_stocktwits_filtered = df_stocktwits_daily[df_stocktwits_daily["brand"] == brand_dropdown]
        df_stocktwits_count_filtered = df_stocktwits_count_daily[df_stocktwits_count_daily["brand"] == brand_dropdown]
        df_yougov_filtered = df_yougov_daily[df_yougov_daily["Brand"] == brand_dropdown]
        title_prefix = "Daily "
        lag_periods, lag_step = 28, 1
        lag_name = "(Days)"
    
    # Link dropdown values to corresponding dataframes
    charts_df = {"Stock Price": df_stocks_filtered, "Stock Price % Change": df_stocks_filtered, "Stock Volume": df_stocks_filtered, "Twitter Polarity": df_tweets_filtered,
                 "Tweets Count": df_tweets_count_filtered, "Stocktwits Polarity": df_stocktwits_filtered, "Stocktwits Count": df_stocktwits_count_filtered}
    yougov_charts_df = {key: df_yougov_filtered for key in yougov_charts.keys()}
    charts_df.update(yougov_charts_df)
    
    x_1 = charts_df[chart_dropdown]["Date"]
    y_1 = charts_df[chart_dropdown][charts[chart_dropdown]]
    x_2 = charts_df[chart_dropdown_2]["Date"] if chart_dropdown_2 != None else None
    y_2 = charts_df[chart_dropdown_2][charts[chart_dropdown_2]] if chart_dropdown_2 != None else None
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=x_1, y=y_1, name=charts_axis_names[chart_dropdown], line=dict(width=1.5),connectgaps = True)
                  ,secondary_y=False)
    title = title_prefix + charts_axis_names[chart_dropdown]
    if chart_dropdown_2 != None:
        title += " vs. " + charts_axis_names[chart_dropdown_2]
        fig.add_trace(go.Scatter(x=x_2, y=y_2, name=charts_axis_names[chart_dropdown_2],line=dict(width=1.5),connectgaps = True,),
                      secondary_y=True)
    
    fig.update_layout(margin={'l': 30, 'b': 40, 't': 30, 'r': 40}, hovermode='x unified', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)',
                    template = "simple_white", showlegend=True,
                    title={
                    'text': title,
                    'y':0.97,
                    'x':0.46,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=0.95,
                                xanchor="right",
                                x=0.94
                                )
            
                    )
    # Round hoverdata to 2 decimal places
    # fig.update_traces(hovertemplate = "%{x}<br>%{y:.2f}")
    fig.update_traces(hovertemplate = "%{y:.2f}")
    fig.update_xaxes(title = "Date")
    fig.update_yaxes(title_text=charts_axis_names[chart_dropdown], secondary_y=False)
    
    # Add second y-axis if second dropdown is selected
    if chart_dropdown_2 != None:
        # Perform Pearson correlation
        r = pearson_correlation(charts_df[chart_dropdown], charts_df[chart_dropdown_2],charts[chart_dropdown], charts[chart_dropdown_2])
        r_str = str(round(r[0],2))
        p = r[1]
        p_str = " ***" if p < 0.001 else " **" if p < 0.01 else " *" if p < 0.05 else " ." if p < 0.1 else ""
        
        fig.update_yaxes(title_text=charts_axis_names[chart_dropdown_2], secondary_y=True)
        fig.add_annotation(dict(font=dict(size=14),
                                        x=0.46,
                                        y=0.96,
                                        showarrow=False,
                                        text="r = " + r_str + p_str,
                                        textangle=0,
                                        xanchor='center',
                                        yanchor='bottom',
                                        xref="paper",
                                        yref="paper"
                                        ))
        
    # fig.update_xaxes(rangeselector_x=0.85, rangeselector_y=1, rangeselector_font_size=11.5)
    # fig.update_layout(xaxis_rangeslider_visible=False)
    if chart_dropdown_2 == None:
        cross_correlation_fig = go.Figure(go.Scatter(
                x=[0],
                y=[0],
                mode="text",
                text=["Select two metrics to view the cross-correlation"],
                textfont=dict(color="black", size=22),
                showlegend=False,
            )
        )

        cross_correlation_fig.update_layout(
            xaxis=dict(showticklabels=False,),
            yaxis=dict(showticklabels=False,),
            # plot_bgcolor="white"
            template="simple_white",paper_bgcolor='rgba(0,0,0,0)', margin={'l': 30, 'b': 40, 't': 30, 'r': 40},
            height=380,
            title={
                        'text': "Cross-correlation",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'}
        )
        
        cross_correlation_fig.update_xaxes(title = "Lag " + lag_name)
        cross_correlation_fig.update_yaxes(title_text= "Correlation")
    
    # Calculate cross-correlation
    elif chart_dropdown_2 != None:
        title = "Cross-Correlation between "  + charts_axis_names[chart_dropdown] + " and " + charts_axis_names[chart_dropdown_2]
        df_cross_correlation = cross_correlation(charts_df[chart_dropdown], charts_df[chart_dropdown_2],charts[chart_dropdown], charts[chart_dropdown_2],lag_periods ,lag_step)
        cross_correlation_fig = go.Figure(data =[
                                                    go.Scatter(x=df_cross_correlation["Lag"],
                                                    y=df_cross_correlation["Correlation"], 
                                                    mode='lines+markers', 
                                                    name="Correlation",
                                                    # hovertemplate = "Correlation: %{y:.2f}",
                                                    showlegend = False,
                                                    # hoverinfo='skip'
                                                    )
                                                ])
        cross_correlation_fig.update_layout(
        hovermode='x',
        hoverlabel=dict(bgcolor="white"),
        template="simple_white",paper_bgcolor='rgba(0,0,0,0)', margin={'l': 40, 'b': 40, 't': 30, 'r': 20},
        height=380,
        title={
                    'text': title,
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top',
                    'font': {"size": 16}},
        yaxis_title_standoff = 0,
        # xaxis_hoverformat = "%{x:.2f} asdsad"
        # showlegend = False
        )
        
        cross_correlation_fig.update_traces(hovertemplate = "%{y:.2f}")
        cross_correlation_fig.update_xaxes(title = f"{chart_dropdown} Lag {lag_name}")
        cross_correlation_fig.update_yaxes(title_text= "Correlation")
        cross_correlation_fig.add_vline(x=0, line_width=2, line_dash="dash", line_color="blue")
    
    return fig, cross_correlation_fig

@callback(Output("brand_sentiment_time_chart","figure"),
              Input("brand-dropdown","value"),
              Input("tabs_sentiment","value"),
              )
def update_brand_sentiment_chart(brand_dropdown,tabs_sentiment):
    brand = brand_dropdown
    if tabs_sentiment == "D":
        df_sentiment = df_tweets_sentiment_daily[df_tweets_sentiment_daily["brand"] == brand]
    elif tabs_sentiment == "W":
        df_sentiment = df_tweets_sentiment_weekly[df_tweets_sentiment_weekly["brand"] == brand]
    else:
        df_sentiment = df_tweets_sentiment_monthly[df_tweets_sentiment_monthly["brand"] == brand]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sentiment["Date"], y=df_sentiment["sentiment_neg_perc"], mode='lines', name='Negative Sentiment', line=dict(color='rgb(248, 79, 49)', width=2), stackgroup='one'))
    fig.add_trace(go.Scatter(x=df_sentiment["Date"], y=df_sentiment["sentiment_pos_perc"], mode='lines', name='Positive Sentiment', line=dict(color='rgb(35, 197, 82)', width=2), stackgroup='one'))
    fig.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 20}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)', height=300,
                    template="simple_white",showlegend=False,
                    yaxis=dict(
                    type='linear',
                    range=[1, 100],
                    ticksuffix='%'),
                    # title ="Monthly Tweets Sentiment",
                    title={
                    'text': "Monthly Twitter Sentiment" if tabs_sentiment == "M" else "Weekly Twitter Sentiment" if tabs_sentiment == "W" else "Daily Twitter Sentiment",
                    'y':0.97,
                    'x':0.53,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    )
    return fig

@callback(Output("brand_sentiment_time_chart_StockTwits","figure"),
              Input("brand-dropdown","value"),
              Input("tabs_sentiment_StockTwits","value"),
              )
def update_brand_sentiment_chart_StockTwits(brand_dropdown,tabs_sentiment):
    brand = brand_dropdown
    if tabs_sentiment == "D":
        df_sentiment_stocktwits = df_stocktwits_daily[df_stocktwits_daily["brand"] == brand]
    elif tabs_sentiment == "W":
        df_sentiment_stocktwits = df_stocktwits_weekly[df_stocktwits_weekly["brand"] == brand]
    else:
        df_sentiment_stocktwits = df_stocktwits_monthly[df_stocktwits_monthly["brand"] == brand]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_sentiment_stocktwits["Date"], y=df_sentiment_stocktwits["negative"], mode='lines', name='Negative Sentiment', line=dict(color='rgb(248, 79, 49)', width=2), stackgroup='one'))
    fig.add_trace(go.Scatter(x=df_sentiment_stocktwits["Date"], y=df_sentiment_stocktwits["positive"], mode='lines', name='Positive Sentiment', line=dict(color='rgb(35, 197, 82)', width=2), stackgroup='one'))
    fig.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 20}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)', height=300,
                    template="simple_white",showlegend=False,
                    yaxis=dict(
                    type='linear',
                    range=[1, 100],
                    ticksuffix='%'),
                    title={
                    'text': "Monthly StockTwits Sentiment" if tabs_sentiment == "M" else "Weekly StockTwits Sentiment" if tabs_sentiment == "W" else "Daily StockTwits Sentiment",
                    'y':0.97,
                    'x':0.53,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    )
    return fig

# Remove dropdown options from second dropdown if they are selected in the first dropdown
@callback(Output("chart-dropdown","options"),
              Output("chart-dropdown-2","options"),
              Input("chart-dropdown","value"),
              Input("chart-dropdown-2","value")
              )
def remove_options_tab2(chart_dropdown_value,chart_dropdown_2_value):
    options = [x for x in dropdown_options_tab2_1 if x != chart_dropdown_2_value]
    options_2 = [x for x in dropdown_options_tab2_2 if x != chart_dropdown_value]
    return options, options_2

# Brand image callback
@callback(Output("brand-image","src"),
              Input("brand-dropdown","value"),
              )
def update_brand_image_srs(brand_dropdown):
    return f"assets/{brand_dropdown}.png"

  
@callback(Output("brand_overall_sentiment","figure"),
              Input("brand-dropdown","value"),
              )
def update_brand_overall_sentiment(brand_dropdown):
    df_sentiment = df_sentiment_overall[df_sentiment_overall["brand"] == brand_dropdown]
    if len(df_sentiment) == 0:
        return go.Figure(data=[])
    labels = ['Positive', 'Negative']
    values = [df_sentiment["sentiment_pos_perc"].values[0], df_sentiment["sentiment_neg_perc"].values[0]]
    middle_text = str(round(df_sentiment["sentiment_pos_perc"].values[0],1)) + "%"
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.55,   )])
    fig.update_traces(hoverinfo='label+percent',textinfo='none',
                      marker=dict(colors=['rgb(35, 197, 82)', 'rgb(248, 79, 49)']))
    fig.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 20}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)', height=300,
                    template="simple_white",showlegend=False,
                    title={
                    'text': "Overall Twitter Sentiment",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    annotations=[dict(text=middle_text, x=0.5, y=0.5, font_size=20, showarrow=False)],
                    )
    return fig

@callback(Output("brand_overall_stocktwits_sentiment","figure"),
              Input("brand-dropdown","value"),
              )
def update_brand_overall_sentiment(brand_dropdown):
    df_sentiment_stocktwits = df_stocktwits_overall[df_stocktwits_overall["brand"] == brand_dropdown]
    if len(df_sentiment_stocktwits) == 0:
        return go.Figure(data=[])
    labels = ['Bullish', 'Bearish']
    values = [df_sentiment_stocktwits["trend"].values[0], abs(df_sentiment_stocktwits["trend"].values[0] - 1)]
    
    middle_text = str(round(df_sentiment_stocktwits["trend"].values[0] * 100,1)) + "%"
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.55,   )])
    fig.update_traces(hoverinfo='label+percent',textinfo='none',
                      marker=dict(colors=['rgb(35, 197, 82)', 'rgb(248, 79, 49)']))
    fig.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 20}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)', height=300,
                    template="simple_white",showlegend=False,
                    title={
                    'text': "Overall StockTwits Sentiment",
                    'y':0.97,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'},
                    annotations=[dict(text=middle_text, x=0.5, y=0.5, font_size=20, showarrow=False)],
                    )
    return fig        

# Callback for the wordcloud
@callback(Output("wordcloud","src"),
              Input("brand-dropdown","value"),
              Input("tabs_wordcloud","value"),
              )  
def update_wordcloud(brand_dropdown, tabs_wordcloud):
    brand_name = brand_dropdown
    polarity = tabs_wordcloud
    image_path = f"data/tab2/wordclouds/{brand_name}_{polarity}_wordcloud_square.png"

    if os.path.exists(image_path):
        source = Image.open(image_path)
    else:
        source = Image.open("data/tab2/wordclouds/wordcloud_placeholder.png")

    return source

# Callback for monthly YouGov charts
@callback(Output("yougov_monthly","figure"),
              Input("brand-dropdown","value"),
              Input("yougov-monthly-dropdown","value"),    
)

def update_yougov_monthlycharts(brand_dropdown,yougov_monthly_dropdown):
    df_yougov = df_yougov_monthly[df_yougov_monthly["Brand"] == brand_dropdown]
    if yougov_monthly_dropdown == "Image":
        yougov_columns = ["Value","Impression","Quality","Recommend","Satisfaction","Reputation"]
    elif yougov_monthly_dropdown == "Pressence":
        yougov_columns = yougov_brand_presence
    elif yougov_monthly_dropdown == "Relationship":
        yougov_columns = yougov_brand_relationship
    fig = go.Figure()
    for i in yougov_columns:
        name_split = str.split(i," ")
        name = "<br>".join(name_split[0:2])
        fig.add_trace(go.Scatter(x=df_yougov["Date"], y=df_yougov[i], mode='lines', name=name, line=dict(width=2),stackgroup='one' if df_yougov[i].min() >= 0 else "two"))
    fig.update_layout(margin={'l': 20, 'b': 20, 't': 30, 'r': 145}, hovermode='x unified', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)', height=380,
                      template="simple_white",showlegend=True,
                      legend=dict(
                        y=0.8,
                        x=1.01
                      ),
                      title={
                        'text': f"Monthly Brand {yougov_monthly_dropdown} Scores",
                        'y':0.97,
                        'x':0.46,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                          
                      
    )
    return fig

# Callback for the radar charts
@callback(Output("brand_overall_relationship", "figure"),
              Input("brand-dropdown","value"),
              Input("radar-dropdown","value")
              )
def update_radar_charts(brand_dropdown,radar_dropdown):
    df_yougov = df_yougov_overall.loc[df_yougov_overall["Brand"] == brand_dropdown]
    df_yougov = df_yougov.drop(columns=["Brand"])
    
    if radar_dropdown == "Pressence":
        # Presence
        df_yougov_pressence = df_yougov[yougov_brand_presence]
        r_pressence = df_yougov_pressence.values[0].tolist()
        theta_pressence = df_yougov_pressence.columns.tolist()
        fig_presence = px.line_polar(df_yougov_pressence, r=r_pressence, theta=theta_pressence, line_close=True,height=380)
        fig_presence.update_layout(margin={'l': 25, 'b': 20, 't': 50, 'r': 50}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        title={
                        'text': "Brand Presence",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        )
        fig_presence.update_traces(fill='toself',
                                mode="lines+markers",
                                hovertemplate = "%{theta} %{r:.2f}")
        # hovertemplate = "%{y:.2f}"
        return fig_presence
    if radar_dropdown == "Image":
        # Image
        df_yougov_image = df_yougov[yougov_brand_image]
        r_image = df_yougov_image.values[0].tolist()
        theta_image = df_yougov_image.columns.tolist()
        fig_image = px.line_polar(df_yougov_image, r=r_image, theta=theta_image, line_close=True,height=380)
        fig_image.update_layout(margin={'l': 55, 'b': 20, 't': 50, 'r': 30}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        title={
                        'text': "Brand Image",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        polar=dict(radialaxis=dict(visible=True, range=[-20, 50])),
                        )
        fig_image.update_traces(fill='toself',
                                mode="lines+markers",
                                hovertemplate = "%{theta} %{r:.2f}")
        return fig_image
    if radar_dropdown == "Relationship":
        # Relationship
        df_yougov_relationship = df_yougov[yougov_brand_relationship]
        r_relationship = df_yougov_relationship.values[0].tolist()
        theta_relationship = yougov_brand_relationship
        fig_relationship = px.line_polar(df_yougov_relationship, r=r_relationship, theta=theta_relationship, line_close=True,height=380)
        fig_relationship.update_layout(margin={'l': 20, 'b': 20, 't': 50, 'r': 30}, hovermode='closest', hoverlabel=dict(bgcolor="white"),paper_bgcolor='rgba(0,0,0,0)',
                        showlegend=False,
                        title={
                        'text': "Brand Relationship",
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        polar=dict(radialaxis=dict(visible=True, range=[0, 50])),
                        
                        )
        fig_relationship.update_traces(fill='toself',
                                        mode="lines+markers",
                                        hovertemplate = "%{theta} %{r:.2f}")
        # Adding new line to the ticktext
        ticks_new_line = ["Consideration", "Purchase<br>Intent", "Current  <br>Customer", "Former  <br>Customer"]
        fig_relationship.update_polars(angularaxis_rotation=45,
                                        angularaxis_ticktext=ticks_new_line,
                                        angularaxis_tickvals=[0,1,2,3],
                                    )
        return fig_relationship
    
    
@callback(Output("upload-data", "style"),
                Input('upload-data', 'contents'),
                State('upload-data', 'filename'),
                # State('upload-data', 'last_modified')
                )
def process_csv(list_of_contents, list_of_names):
    recalculate_twitter = False
    recalculate_stocktwits = False
    if list_of_names is not None:
        for contents, name in zip(list_of_contents, list_of_names):
            if name.endswith('.csv'):
        
                # Check if the file is a CSV
                # if name.endswith('.csv'):
                if name == "YouGov.csv":
                    name = "yougov.csv"
                    yougov_directory = "data/tab2/new_YouGov/"
                    process_data_file(name, contents, yougov_directory,yougov_to_df)
                elif name == "Stocks_daily.csv":
                    stocks_directory = "data/tab2/new_stocks/"
                    process_data_file(name, contents, stocks_directory,None)
                elif name == "Stocks_weekly.csv":
                    stocks_directory = "data/tab2/new_stocks/"
                    process_data_file(name, contents, stocks_directory,None)
                        
                else:
                    # Extract the brand and data source from the filename
                    brand, data_source = name.split('_')
                    data_source = os.path.splitext(data_source)[0]
                    directory = f"data/tab2/new_{data_source}/{brand}/"
                    
                    if data_source == "tweets":
                        recalculate_twitter = True
                        process_data_file (name, contents, directory, tweets_to_df)
                        # if not os.path.exists(directory):
                        #     os.makedirs(directory)
                            
                        # prefix, base64_string = contents.split(',', 1)
                        # assert prefix == "data:text/csv;base64"

                        # # Decode the base64-encoded CSV data
                        # decoded = base64.b64decode(base64_string)

                        # # # Convert the decoded bytes to a string
                        # # decoded_str = decoded.decode('utf-8')
                        
                        # # Load the CSV data into a Pandas DataFrame
                        # # csv_rows = list(csv.reader(decoded_str.splitlines()))
                        # df_new_tweets = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                        # df_new_tweets["brand"] = brand
                        # # df_new_tweets.to_csv(os.path.join(directory, name), index=False)
                        
                        # # Check if the file already exists
                        # if os.path.isfile(os.path.join(directory, name)):
                        #     # If the file exists, read it as a pandas DataFrame
                        #     df_existing_tweets = pd.read_csv(os.path.join(directory, name))
                            
                        #     # Concatenate the new DataFrame with the existing DataFrame
                        #     df_concatenated_tweets = pd.concat([df_existing_tweets, df_new_tweets], ignore_index=True)
                        #     df_concatenated_tweets = df_concatenated_tweets.drop_duplicates()
                            
                        #     # Write the concatenated DataFrame to the CSV file
                        #     df_concatenated_tweets.to_csv(os.path.join(directory, name), index=False)
                        #     tweets_to_df(name,directory,df_concatenated_tweets)
                            
                        # else:
                        #     # If the file does not exist, write the new DataFrame to the CSV file
                        #     df_new_tweets.to_csv(os.path.join(directory, name), index=False)
                        #     tweets_to_df(name,directory,df_new_tweets)

                    elif data_source == "stocktwits":
                        recalculate_stocktwits = True
                        # if not os.path.exists(directory):
                        #     os.makedirs(directory)
                        # prefix, base64_string = contents.split(',', 1)
                        # assert prefix == "data:text/csv;base64"

                        # # Decode the base64-encoded CSV data
                        # decoded = base64.b64decode(base64_string)
                        
                        # df_new_stocktwits = pd.read_csv(io.StringIO(decoded.decode('utf-8')),delimiter=";")
                        # df_new_stocktwits["brand"] = brand

                        # # Define the delimiters to try
                        # delimiters = [',', ';']

                        # # Iterate over the delimiters and try reading the data
                        # for delimiter in delimiters:
                        #     try:
                        #         df_new_stocktwits = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=delimiter)
                        #         # If reading succeeds, break the loop
                        #         break
                        #     except pd.errors.ParserError:
                        #         continue                        
                        
                        # if os.path.isfile(os.path.join(directory, name)):
                        #     # If the file exists, read it as a pandas DataFrame
                        #     df_existing_stocktwits = pd.read_csv(os.path.join(directory, name))
                            
                        #     # Concatenate the new DataFrame with the existing DataFrame
                        #     df_concatenated_stocktwits = pd.concat([df_existing_stocktwits, df_new_stocktwits], ignore_index=True)
                        #     df_concatenated_stocktwits = df_concatenated_stocktwits.drop_duplicates()
                            
                        #     # Write the concatenated DataFrame to the CSV file
                        #     df_concatenated_stocktwits.to_csv(os.path.join(directory, name), index=False)
                        #     stocktwits_to_df(name,directory,df_concatenated_stocktwits)
                            
                        # else:
                        #     # If the file does not exist, write the new DataFrame to the CSV file
                        #     df_new_stocktwits.to_csv(os.path.join(directory, name), index=False)
                        #     stocktwits_to_df(name,directory,df_new_stocktwits)
                        process_data_file(name, contents, directory, stocktwits_to_df)
            # Save Brand Logo
            elif name.endswith('.png'):
                data = contents.encode("utf8").split(b";base64,")[1]
                if not os.path.isfile("assets/"+name):
                    with open("assets/"+name, "wb") as fp:
                        fp.write(base64.decodebytes(data))
                    
        if recalculate_twitter or recalculate_stocktwits:
            recalculate_values(recalculate_twitter,recalculate_stocktwits)
                    
                    
    
    return {
                    'width': '100%',
                    'height': '30px',
                    'lineHeight': '30px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                }