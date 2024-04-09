import numpy as np
import pandas as pd


def initialise_df(*column_names):
    """
    Initialise a pandas dataframe with n column names.

    Parameters
    ----------
    *column_names : str
        N column names

    Returns
    -------
    pd.DataFrame
        Empty pandas dataframe with specified column names
    """
    return pd.DataFrame(columns=column_names)


def sanitise_df(df):
    """
    Replaces infinite values in a dataframe with NaN.

    Parameters
    ----------
    df : pd.DataFrame
        Any dataframe

    Returns
    -------
    pd.DataFrame
        Dataframe with Inf replaced with NaN.
    """
    df = df.replace(np.inf, np.nan)
    return df


def safe_pandas_concat(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """
    Concatenate two DataFrames without relying on deprecated functionality
    when one of the DataFrames is empty.

    If df1 and df2 are non-empty, return the concatenation. df2 will extend df1
    in the resulting DataFrame.
    If df1 is empty and df2 is not, return a copy of df2.
    If df1 is non-empty and df2 is, return a copy of df1.
    If df1 and df2 are empty, return an empty DataFrame with the same column
    names as df1.

    Parameters
    ----------
    df1 : pd.DataFrame
        DataFrame to concatenate.
    df2 : pd.DataFrame
        DataFrame to concatenate.

    Returns
    -------
    pd.DataFrame
        DataFrame formed from concatenation of df1 and df2.
    """
    if df1.empty and df2.empty:
        return pd.DataFrame(columns=df1.columns)
    elif df1.empty:
        return df2.copy()
    elif df2.empty:
        return df1.copy()
    else:
        return pd.concat([df1, df2], ignore_index=True)
