import pandas as pd
import pytest
from qtpy.QtCore import Qt

from brainglobe_utils.qtpy.table import DataFrameModel


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {"A": [1, 2, 3], "B": ["cat", "dog", "rabbit"], "C": [7, 8, 9]}
    )


@pytest.fixture
def model(sample_df):
    return DataFrameModel(sample_df)


def test_row_count(model, sample_df):
    assert model.rowCount() == sample_df.shape[0]


def test_column_count(model, sample_df):
    assert model.columnCount() == sample_df.shape[1]


def test_data(model):
    index = model.index(0, 0)
    assert model.data(index, Qt.DisplayRole) == "1"
    index = model.index(1, 1)
    assert model.data(index, Qt.DisplayRole) == "dog"
    index = model.index(2, 2)
    assert model.data(index, Qt.DisplayRole) == "9"

    assert model.data(index, Qt.EditRole) is None


def test_header_data(model, sample_df):
    assert (
        model.headerData(0, Qt.Vertical, Qt.DisplayRole) == sample_df.index[0]
    )
    assert (
        model.headerData(1, Qt.Vertical, Qt.DisplayRole) == sample_df.index[1]
    )
    assert (
        model.headerData(2, Qt.Vertical, Qt.DisplayRole) == sample_df.index[2]
    )
