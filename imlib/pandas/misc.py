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
