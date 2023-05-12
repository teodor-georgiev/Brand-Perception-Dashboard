import plotly.express as px
from scipy import stats
import pandas as pd

# Function to annotate the plot
def create_annotations(df: dict, xaxis: str, yaxis: str)->list:
    """
    Adds annotations to the plot

    Parameters
    ----------
    df : dict
        Dataframe with the data
    xaxis : str
        Name of the column to be used as x-axis
    yaxis : str
        Name of the column to be used as y-axis

    Returns
    -------
    annotations : List
        List with the annotations
    """    
    annotations = []
    first = True
    for index, row in df.iterrows():
        if first:
            col = "black"
            first = False
        else:
            col = "black"
                
        anno = dict(x=row[xaxis],
                    y=row[yaxis],
                    text=row["Brand Name"],
                    showarrow=False,
                    arrowhead=0,
                    font=dict(color=col),
                    yshift=25,
                    bgcolor="white",
                    opacity=0.85)

        annotations.append(anno)
    return annotations

def create_boxplot(df: dict, axis: str,axis_titles, color_map)->object:
    """
    Creates a boxplot

    Parameters
    ----------
    df : dict
        Dataframe with the data
    axis : str
        Axis to be used

    Returns
    -------
    object
        Object with the plot
    """    
    fig = px.box(df, x="Sector", y=axis, color="Sector",  color_discrete_map= color_map, height = 280,
                       template = "simple_white")
    fig.update_yaxes(title = axis_titles)
    fig.update_layout (  
                        margin={'l': 40, 'b': 40, 't': 30, 'r': 18},
                        boxgap= 0.8 if df["Sector"].nunique() < 3 else 0.6 if df["Sector"].nunique() < 4 else 0.3,
                        # Make the plot background transparent
                        paper_bgcolor='rgba(0,0,0,0)',
                        title={
                        'text': "Boxplot of " + axis,
                        'y':0.97,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'},
                        yaxis_tickformat=",.3f"
                    
                        )
    return fig


def pearson_correlation(df_1: pd.DataFrame, df_2: pd.DataFrame, column_name_1: str, column_name_2: str) -> tuple:
    """
    Function to calculate the pearson correlation between two columns

    Parameters
    ----------
    df_1 : pd.DataFrame
        First dataframe containing the time series
    df_2 : pd.DataFrame
        Second dataframe containing the time series
    column_name_1 : str
        Name of the column to be used from the first dataframe
    column_name_2 : str
        Name of the column to be used from the second dataframe

    Returns
    -------
    r : tuple
        Tuple with the correlation and the p-value
    """    
    
    df_1 = df_1[['Date', column_name_1]]
    df_2 = df_2[['Date', column_name_2]]
    df_correlate = pd.merge(df_1, df_2, on='Date', how='inner')
    df_correlate = df_correlate.dropna()
    if len(df_correlate) <= 2:
        return (0, 1)
    # x = df_correlate[column_name_1]
    # y = df_correlate[column_name_2]
    r = stats.pearsonr(df_correlate[column_name_1], df_correlate[column_name_2])
    return r

def cross_correlation(df_1: pd.DataFrame, df_2: pd.DataFrame, column_name_1: str, column_name_2: str, lag_periods: int, lag_step: int) -> pd.DataFrame:
    """
    Function to calculate the cross correlation between two time series

    Parameters
    ----------
    df_1 : pd.DataFrame
        First dataframe containing the time series
    df_2 : pd.DataFrame
        Second dataframe containing the time series
    column_name_1 : str
        Name of the column to be used from the first dataframe
    column_name_2 : str
        Name of the column to be used from the second dataframe
    lag_periods : int
        Number of lag periods to be used (both positive and negative)
    lag_step : int
        Lag step to be used. 1 means that the lag will be calculated for each day, 7 means that the lag will be calculated for each week

    Returns
    -------
    df_cross_correlation : pd.DataFrame
        Dataframe containing the lag, correlation and p-value for each lag period
    """    
    df_cross_correlation = pd.DataFrame({"Lag" : [], "Correlation" : [], "P-value" :[]})
    first_df = df_1.copy()
    second_df = df_2.copy()
    for i in range(-lag_periods, lag_periods + 1, lag_step):
        df_1 = first_df[['Date', column_name_1]]
        df_2 = second_df[['Date', column_name_2]]


        df_1['Date'] = pd.to_datetime(df_1['Date'])
        df_2['Date'] = pd.to_datetime(df_2['Date'])
        df_1["Date"] += pd.DateOffset(days=i)

        df_correlate = pd.merge(df_1, df_2, on='Date', how='inner')
        df_correlate = df_correlate.dropna()
        if len(df_correlate) > 2:
            r = stats.pearsonr(df_correlate[column_name_1], df_correlate[column_name_2])

            # Create a dataframe with the results
            df_cross_correlation = pd.concat([df_cross_correlation, pd.DataFrame({"Lag" : [i], "Correlation" : [r[0]], "P-value" :[r[1]]})], ignore_index=True)
    df_cross_correlation["Lag"] = df_cross_correlation["Lag"]/lag_step
    return df_cross_correlation


def calculate_sentiment_percentages(df, neg_col, pos_col):
    total = df[neg_col] + df[pos_col]
    df[f"{neg_col}_perc"] = ((df[neg_col] / total) * 100).round(2)
    df[f"{pos_col}_perc"] = ((df[pos_col] / total) * 100).round(2)
    return df


def raw_tweets_to_df(file):
    # Read csv file
    df_file = pd.read_csv(file, sep=";")
    
    # Select relevant columns
    columns = ["date", "sentiment_neg", "sentiment_neu", "sentiment_pos"]
    df_tweets = df_file[[col for col in df_file.columns if col in columns]]

    # Set brand name and drop rows with missing values
    df_tweets["brand"] = "Airbnb"
    df_tweets = df_tweets.dropna()

    # Set date format
    df_tweets["date"] = pd.to_datetime(df_tweets["date"], format="%Y-%m-%d")
    df_tweets["date"] = df_tweets["date"].dt.strftime("%Y-%m-%d")

    # Replace , with . and convert to float
    df_tweets["sentiment_neg"] = df_tweets["sentiment_neg"].str.replace(",", ".").astype(float)
    df_tweets["sentiment_pos"] = df_tweets["sentiment_pos"].str.replace(",", ".").astype(float)
    df_tweets["sentiment_neu"] = df_tweets["sentiment_neu"].str.replace(",", ".").astype(float)
    
    # Calculate overall sentiment
    df_sentiment_overall = df_tweets[["brand","sentiment_neg","sentiment_pos"]].groupby("brand").mean().reset_index()
    df_sentiment_overall = calculate_sentiment_percentages(df_sentiment_overall, "sentiment_neg", "sentiment_pos")
    
    # Calculate daily sentiment and polarity
    df_sentiment_day = df_tweets.groupby(["brand", "date"]).mean().reset_index()
    df_sentiment_day = calculate_sentiment_percentages(df_sentiment_day, "sentiment_neg", "sentiment_pos")
    # df_sentiment_day["sentiment_neg_perc"] = ((df_sentiment_day["sentiment_neg"] / (df_sentiment_day["sentiment_neg"] + df_sentiment_day["sentiment_pos"]))*100).round(2)
    # df_sentiment_day["sentiment_pos_perc"] = ((df_sentiment_day["sentiment_pos"] / (df_sentiment_day["sentiment_neg"] + df_sentiment_day["sentiment_pos"]))*100).round(2)
    
    df_sentiment_day["polarity"] = df_sentiment_day["sentiment_pos_perc"] - df_sentiment_day["sentiment_neg_perc"]
    df_sentiment_day.rename(columns={"date":"Date"}, inplace=True)
    df_sentiment_day = df_sentiment_day.dropna()
    
    # Calculate weekly polarity
    df_tweets["date"] = pd.to_datetime(df_tweets["date"], format="%Y-%m-%d")
    df_sentiment_week = df_tweets.groupby(["brand", pd.Grouper(key="date", freq="W-SUN")]).mean().reset_index()
    df_sentiment_week.rename(columns={"date":"Date"}, inplace=True)
    df_sentiment_week["Date"] -= pd.to_timedelta(6, unit="d")
    df_sentiment_week = calculate_sentiment_percentages(df_sentiment_week, "sentiment_neg", "sentiment_pos")
    # df_sentiment_week["sentiment_neg_perc"] = ((df_sentiment_week["sentiment_neg"] / (df_sentiment_week["sentiment_neg"] + df_sentiment_week["sentiment_pos"]))*100).round(2)
    # df_sentiment_week["sentiment_pos_perc"] = ((df_sentiment_week["sentiment_pos"] / (df_sentiment_week["sentiment_neg"] + df_sentiment_week["sentiment_pos"]))*100).round(2)
    df_sentiment_week["polarity"] = df_sentiment_week["sentiment_pos_perc"] - df_sentiment_week["sentiment_neg_perc"]
    df_sentiment_week = df_sentiment_week.dropna()
    
    # Calculate monthly polarity
    df_sentiment_month = df_tweets.groupby(["brand", pd.Grouper(key="date", freq="M")]).mean().reset_index()
    df_sentiment_month.rename(columns={"date":"Date"}, inplace=True)
    df_sentiment_month = calculate_sentiment_percentages(df_sentiment_month, "sentiment_neg", "sentiment_pos")
    # df_sentiment_month["sentiment_neg_perc"] = ((df_sentiment_month["sentiment_neg"] / (df_sentiment_month["sentiment_neg"] + df_sentiment_month["sentiment_pos"]))*100).round(2)
    # df_sentiment_month["sentiment_pos_perc"] = ((df_sentiment_month["sentiment_pos"] / (df_sentiment_month["sentiment_neg"] + df_sentiment_month["sentiment_pos"]))*100).round(2)
    df_sentiment_month["polarity"] = df_sentiment_month["sentiment_pos_perc"] - df_sentiment_month["sentiment_neg_perc"]
    df_sentiment_month.dropna(inplace=True)
    
    return df_sentiment_day, df_sentiment_week, df_sentiment_month, df_sentiment_overall

