import numpy as np
import pandas as pd

from brainglobe_utils.pandas import misc as pandas_misc

columns = ["name", "number"]
data_with_nan = [["one", np.nan], ["two", 15], ["three", np.nan]]
df_with_nan = pd.DataFrame(data_with_nan, columns=columns)
data_with_inf = [["one", np.inf], ["two", 15], ["three", np.inf]]
df_with_inf = pd.DataFrame(data_with_inf, columns=columns)


def test_initialise_df():
    test_df = pandas_misc.initialise_df("one", "two", "3")
    df = pd.DataFrame(columns=["one", "two", "3"])
    assert df.equals(test_df)


def test_sanitise_df():
    sanitised_df = pandas_misc.sanitise_df(df_with_inf)
    assert sanitised_df.equals(df_with_nan)


def test_safe_pandas_concat() -> None:
    """
    Test the following:
    - Non-empty dataframes are concatenated as expected,
    - When one dataframe is empty, the other is returned,
    - When both dataframes are empty, an empty dataframe with
    the corresponding columns is returned.
    """
    df1 = pd.DataFrame(data={"a": [1], "b": [2], "c": [3]})
    df2 = pd.DataFrame(data={"a": [4], "b": [5], "c": [6]})
    empty_df = pd.DataFrame(columns=["a", "b", "c"])
    combined_df = pd.DataFrame(data={"a": [1, 4], "b": [2, 5], "c": [3, 6]})

    assert combined_df.equals(pandas_misc.safe_pandas_concat(df1, df2))
    assert df1.equals(pandas_misc.safe_pandas_concat(df1, empty_df))
    assert df2.equals(pandas_misc.safe_pandas_concat(empty_df, df2))
    assert empty_df.equals(pandas_misc.safe_pandas_concat(empty_df, empty_df))
