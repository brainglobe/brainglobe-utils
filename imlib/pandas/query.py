import numpy as np


def column_as_array(df, column_name):
    """
    Returns an array of a specific dataframe column
    :param df: Dataframe to be queried
    :param column_name: Dataframe column heading to be queried
    :return np.array: Resulting array of query
    """
    return np.array(df[column_name])
