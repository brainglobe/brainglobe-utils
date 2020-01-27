import pandas as pd
import numpy as np

from imlib.pandas import misc as pandas_misc


def test_initialise_df():
    test_df = pandas_misc.initialise_df("one", "two", "3")
    df = pd.DataFrame(columns=["one", "two", "3"])
    assert df.equals(test_df)


def test_sanitise_df():
    columns = ["name", "number"]

    data_with_nan = [["one", np.nan], ["two", 15], ["three", np.nan]]
    df_with_nan = pd.DataFrame(data_with_nan, columns=columns)

    data_with_inf = [["one", np.inf], ["two", 15], ["three", np.inf]]
    df_with_inf = pd.DataFrame(data_with_inf, columns=columns)
    sanitised_df = pandas_misc.sanitise_df(df_with_inf)

    assert sanitised_df.equals(df_with_nan)
