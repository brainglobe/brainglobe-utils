import pandas as pd
import numpy as np

from imlib.pandas import query as pandas_query


def test_column_as_array():
    columns = ["name", "number"]
    data = [["one", 1], ["two", 8.6], ["three", 100]]
    df = pd.DataFrame(data, columns=columns)
    array = np.array([1, 8.6, 100])
    assert (pandas_query.column_as_array(df, columns[1]) == array).all()
