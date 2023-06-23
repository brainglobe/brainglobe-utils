import numpy as np
import pandas as pd
import pytest

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


def test_move_column_first():
    column_first = pandas_misc.move_column_first(df_with_nan, "number")
    assert column_first.columns[0] == columns[1]
    assert column_first[columns[1]][1] == 15

    with pytest.raises(ValueError):
        pandas_misc.move_column_first(data_with_nan, "number")

    with pytest.raises(ValueError):
        pandas_misc.move_column_first(df_with_nan, columns)
