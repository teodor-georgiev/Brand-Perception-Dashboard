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

