import numpy as np
import pandas as pd


def initialise_df(*column_names):
    """
    Initialise a pandasdataframe with n column names
    :param str column_names: N column names
    :return: Empty pandas dataframe with specified column names
    """
    return pd.DataFrame(columns=column_names)


def sanitise_df(df):
    """
    Replaces infinite values in a dataframe with NaN
    :param df: Any dataframe
    :return: Dataframe with Inf replaced with NaN
    """
    df = df.replace(np.inf, np.nan)
    return df


def move_column_first(df, column_name):
    """
    Moves a given dataframe column (given by name) to the first position
    :param df: Dataframe
    :param str column_name: Column name
    :return: Dataframe with new first column
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a dataframe!")
    if not isinstance(column_name, str):
        raise ValueError("column_name must be a string!")
    col = df[column_name]
    df.drop(labels=[column_name], axis=1, inplace=True)
    df.insert(0, column_name, col)
    return df


def regex_remove_df_columns(df, search_string_list):
    """
    Remove columns in a dataframe based on a list of search strings
    :param df: Pandas dataframe
    :param search_string_list: A list of regex strings to search for.
    Columns matching these will be removed
    """
    for search_string in search_string_list:
        df = df.drop(df.filter(regex=search_string).columns, axis=1)
    return df


def safe_pandas_concat(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate two DataFrames without relying on deprecated functionality
    when one of the DataFrames is empty.
    If df1 and df2 are non-empty, return the concatenation.
    If df1 is empty and df2 is not, return a copy of df2.
    If df1 is non-empty and df2 is, return a copy of df1.
    If df1 and df2 are empty, return an empty DataFrame with the same column
    names as df1.
    :param df1: DataFrame to concatenate.
    :param df2: DataFrame to concatenate.
    :returns: DataFrame formed from concatenation of df1 and df2.
    """
    if df1.empty and df2.empty:
        return pd.DataFrame(columns=df1.columns)
    elif df1.empty:
        return df2.copy()
    elif df2.empty:
        return df1.copy()
    else:
        return pd.concat([df1, df2], ignore_index=True)
