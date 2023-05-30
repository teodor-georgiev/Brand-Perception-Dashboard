import plotly.express as px
from scipy import stats
import pandas as pd
import os, glob
import base64, io

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


def tweets_to_df(filename,path,df):
    brand = str(filename.split("_")[0])
    # type = str(filename.split("_")[1].split(".")[0])
    
    # Read csv file
    df_tweets = df
    
    # Select only relevant columns
    columns = ["date", "sentiment_neg", "sentiment_neu", "sentiment_pos"]
    df_tweets = df_tweets[[col for col in df_tweets.columns if col in columns]]

    # Replace , with . and convert to float
    df_tweets["sentiment_neg"] = df_tweets["sentiment_neg"].str.replace(",", ".").astype(float)
    df_tweets["sentiment_pos"] = df_tweets["sentiment_pos"].str.replace(",", ".").astype(float)
    df_tweets["sentiment_neu"] = df_tweets["sentiment_neu"].str.replace(",", ".").astype(float)

    # Set date format
    df_tweets["date"] = pd.to_datetime(df_tweets["date"], format="%Y-%m-%d")
    df_tweets["date"] = df_tweets["date"].dt.strftime("%Y-%m-%d")

    # Set brand name and drop rows with missing values
    df_tweets["brand"] = brand

    df_tweets_all = df_tweets
    # Remove rows with no sentiment
    df_tweets = df_tweets.dropna()
    df_tweets_all = df_tweets_all.fillna(0)
    
    # Calculate overall sentiment
    # df_sentiment_overall = df_tweets[["brand","sentiment_neg","sentiment_pos"]].groupby("brand").mean().reset_index()
    # df_sentiment_overall = calculate_sentiment_percentages(df_sentiment_overall, "sentiment_neg", "sentiment_pos")
    
    # Calculate daily sentiment and polarity
    df_sentiment_day = df_tweets.groupby(["brand", "date"]).mean().reset_index().round(3)
    df_sentiment_day = calculate_sentiment_percentages(df_sentiment_day, "sentiment_neg", "sentiment_pos")
    df_sentiment_day["polarity"] = df_sentiment_day["sentiment_pos_perc"] - df_sentiment_day["sentiment_neg_perc"]
    df_sentiment_day.rename(columns={"date":"Date"}, inplace=True)
    df_sentiment_day = df_sentiment_day.dropna()
    df_sentiment_day.to_csv(path + brand + "_twitter_sentiment_day_percent.csv", index=False)
    
    # Calculate weekly polarity
    df_tweets["date"] = pd.to_datetime(df_tweets["date"], format="%Y-%m-%d")
    df_sentiment_week = df_tweets.groupby(["brand", pd.Grouper(key="date", freq="W-SUN")]).mean().reset_index()
    df_sentiment_week.rename(columns={"date":"Date"}, inplace=True)
    df_sentiment_week["Date"] -= pd.to_timedelta(6, unit="d")
    df_sentiment_week = calculate_sentiment_percentages(df_sentiment_week, "sentiment_neg", "sentiment_pos")
    df_sentiment_week["polarity"] = df_sentiment_week["sentiment_pos_perc"] - df_sentiment_week["sentiment_neg_perc"]
    df_sentiment_week = df_sentiment_week.dropna()
    df_sentiment_week.to_csv(path + brand + "_twitter_sentiment_week_percent.csv", index=False)
    
    # Calculate monthly polarity
    df_sentiment_month = df_tweets.groupby(["brand", pd.Grouper(key="date", freq="M")]).mean().reset_index()
    df_sentiment_month.rename(columns={"date":"Date"}, inplace=True)
    df_sentiment_month = calculate_sentiment_percentages(df_sentiment_month, "sentiment_neg", "sentiment_pos")
    

    df_sentiment_month["polarity"] = df_sentiment_month["sentiment_pos_perc"] - df_sentiment_month["sentiment_neg_perc"]
    df_sentiment_month.dropna(inplace=True)
    df_sentiment_month.to_csv(path + brand + "_twitter_sentiment_month_percent.csv", index=False)
    
    # Calculate daily tweet count
    df_tweets_count_daily = df_tweets_all[["brand",	"date",	"sentiment_neg"]].groupby(["brand", "date"]).count().reset_index()
    df_tweets_count_daily.rename(columns={"date":"Date", "sentiment_neg":"tweet_count"}, inplace=True)
    df_tweets_count_daily.to_csv(path + brand + "_twitter_count_daily.csv", index=False)
    
    # Calculate weekly tweet count
    df_tweets_all["date"] = pd.to_datetime(df_tweets_all["date"], format="%Y-%m-%d")
    df_tweets_count_weekly = df_tweets_all[["brand","date",	"sentiment_neg"]].groupby(["brand", pd.Grouper(key="date", freq="W-SUN")]).count().reset_index()
    df_tweets_count_weekly.rename(columns={"date":"Date", "sentiment_neg":"tweet_count"}, inplace=True)
    df_tweets_count_weekly["Date"] -= pd.to_timedelta(6, unit="d")
    df_tweets_count_weekly.to_csv(path + brand + "_twitter_count_weekly.csv", index=False)
    
        
    return None

def yougov_to_df(filename,path,df):
    df_yougov_daily = df
    
    # df_yougov_daily["Date"] = df_yougov_daily["Date"].dt.strftime("%Y-%m-%d")
    df_yougov_daily["Date"] = pd.to_datetime(df_yougov_daily["Date"], format="%Y-%m-%d")
    df_yougov_daily.to_csv(path + filename + "_daily.csv", index=False)
    
    df_yougov_weekly = df_yougov_daily.groupby(["Brand", pd.Grouper(key="Date", freq="W-SUN")]).mean().reset_index().round(1)
    # df_yougov_weekly["Date"].pd_to_datetime(df_yougov_weekly["Date"], format="%Y-%m-%d")
    df_yougov_weekly["Date"] -= pd.to_timedelta(6, unit="d")
    df_yougov_weekly.to_csv(path + filename + "_weekly.csv", index=False)
    
    df_yougov_monthly = df_yougov_daily.groupby(["Brand", pd.Grouper(key="Date", freq="M")]).mean().reset_index().round(1)
    df_yougov_monthly.to_csv(path + filename + "_monthly.csv", index=False)
    
    return None

def stocktwits_to_df(filename,path,df):
    
    brand = str(filename.split("_")[0])
    # type = str(file.split("_")[1].split(".")[0])
    
    df_stocktwits = df
    df_stocktwits["brand"] = brand
    
    df_stocktwits["bullish"] = (df_stocktwits["trend"] == "Bullish").astype(int)
    df_stocktwits["bearish"] = (df_stocktwits["trend"] == "Bearish").astype(int)
    df_stocktwits.rename(columns={"date":"Date"}, inplace=True)
    df_stocktwits["Date"] = pd.to_datetime(df_stocktwits["Date"])
    
    
    # Select only relevant columns
    columns = ["Date", "brand", "bullish", "bearish"]
    df_stocktwits = df_stocktwits[[col for col in df_stocktwits.columns if col in columns]]
    df_stocktwits["Date"] = df_stocktwits["Date"].dt.date
    
    # Calculate daily polarity
    df_stocktwits_daily = df_stocktwits[["brand","bullish","bearish","Date"]].groupby(["brand","Date"]).sum().reset_index()
    df_stocktwits_daily["polarity"] = (df_stocktwits_daily["bullish"] - df_stocktwits_daily["bearish"])/(df_stocktwits_daily["bullish"] + df_stocktwits_daily["bearish"])*100
    df_stocktwits_daily = df_stocktwits_daily.dropna()
    df_stocktwits_daily["polarity"] = df_stocktwits_daily["polarity"].round(2)
    df_stocktwits_daily.to_csv(path + brand + "_stocktwits_daily.csv", index=False)
    
    # Calculate weekly polarity
    df_stocktwits["Date"] = pd.to_datetime(df_stocktwits["Date"])
    df_stocktwits_weekly = df_stocktwits.groupby(["brand", pd.Grouper(key="Date", freq="W-SUN")]).sum().reset_index()
    df_stocktwits_weekly["Date"] -= pd.to_timedelta(6, unit="d")
    df_stocktwits_weekly["polarity"] = (df_stocktwits_weekly["bullish"] - df_stocktwits_weekly["bearish"])/(df_stocktwits_weekly["bullish"] + df_stocktwits_weekly["bearish"])*100
    df_stocktwits_weekly["polarity"] = df_stocktwits_weekly["polarity"].round(2)
    df_stocktwits_weekly.to_csv(path + brand + "_stocktwits_weekly.csv", index=False)

    # Calculate monthly polarity
    df_stocktiwts_monthly = df_stocktwits.groupby(["brand", pd.Grouper(key="Date", freq="M")]).sum().reset_index()
    df_stocktiwts_monthly["polarity"] = (df_stocktiwts_monthly["bullish"] - df_stocktiwts_monthly["bearish"])/(df_stocktiwts_monthly["bullish"] + df_stocktiwts_monthly["bearish"])*100
    df_stocktiwts_monthly["polarity"] = df_stocktiwts_monthly["polarity"].round(2)
    df_stocktiwts_monthly.to_csv(path + brand + "_stocktwits_monthly.csv", index=False)

    # Count of stocktwits per day
    df_stocktwits_daily_count = df_stocktwits[["brand","bullish","bearish","Date"]].groupby(["brand","Date"]).count().reset_index()
    df_stocktwits_daily_count.to_csv(path + brand + "_stocktwits_daily_count.csv", index=False)
    # Count of stocktwits per week
    df_stocktwits_weekly_count = df_stocktwits.groupby(["brand", pd.Grouper(key="Date", freq="W-SUN")]).count().reset_index()
    df_stocktwits_weekly_count["Date"] -= pd.to_timedelta(6, unit="d")
    df_stocktwits_weekly_count.to_csv(path + brand + "_stocktwits_weekly_count.csv", index=False)
    
    return None

def recalculate_values(twitter_bool,stocktwits_bool):
    paths = []
    
    if twitter_bool:
        paths.append(r"data/tab2/new_tweets/")
    
    if stocktwits_bool:
        paths.append(r"data/tab2/new_stocktwits/")
        
    for path in paths:
        files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)

    if len(files) != 0:
        # Define a dictionary to store the concatenated DataFrames for each brand and data type
        data_type_dict = {}
        exclude = ["tweets", "stocktwits"]

        for file in files:
            # Extract the file name and data type from the file path
            file_name = os.path.splitext(os.path.basename(file))[0]
            data_type = file_name.split("_", 1)[1]
            
            if data_type not in data_type_dict and data_type not in exclude:
                data_type_dict[data_type] = pd.read_csv(file)
            elif data_type not in exclude:
                data_type_dict[data_type] = pd.concat([data_type_dict[data_type], pd.read_csv(file)])
                
    # Save the concatenated DataFrames to csv files
    for data_key in data_type_dict.keys():
        data_type_dict[data_key].to_csv(path + data_key + ".csv", index=False)
        

def update_data(name, data_directory, df_new_data, data_to_df_func=None):
    
    file_path = os.path.join(data_directory, name)
    
    if os.path.isfile(file_path):
        # If the file exists, read it as a pandas DataFrame
        df_existing_data = pd.read_csv(file_path)
        
        # Concatenate the new DataFrame with the existing DataFrame
        df_concatenated_data = pd.concat([df_existing_data, df_new_data], ignore_index=True)
        df_concatenated_data = df_concatenated_data.drop_duplicates()
        
        # Write the concatenated DataFrame to the CSV file
        df_concatenated_data.to_csv(file_path, index=False)
        
        if data_to_df_func is not None:
            data_to_df_func(name, data_directory, df_concatenated_data)
        
    else:
        # If the file does not exist, write the new DataFrame to the CSV file
        df_new_data.to_csv(file_path, index=False)
        
        if data_to_df_func is not None:
            data_to_df_func(name, data_directory, df_new_data)

def process_data_file(name, contents, data_directory,data_to_df_func):
    """
    _summary_

    Parameters
    ----------
    name : _type_
        _description_
    contents : _type_
        _description_
    data_directory : _type_
        _description_
    """    
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    prefix, base64_string = contents.split(',', 1)
    assert prefix == "data:text/csv;base64"
    decoded = base64.b64decode(base64_string)
    
    delimiters = [',', ';']
    
    # Iterate over the delimiters and try reading the data
    for delimiter in delimiters:
        try:
            df_new_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=delimiter)
            # If reading succeeds, break the loop
            break
        except pd.errors.ParserError:
            continue    
    # df_new_data = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    # Check if the file already exists
    update_data(name, data_directory, df_new_data, data_to_df_func)

def concatenate_df (df, new_df_path, brand_column):
    df = pd.concat([df, pd.read_csv(new_df_path)])
    df.drop_duplicates(inplace = True)
    df.sort_values(by = [brand_column, "Date"], inplace = True)
    return df
    
    
            

