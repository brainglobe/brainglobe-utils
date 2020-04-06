import pandas as pd
import numpy as np


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
