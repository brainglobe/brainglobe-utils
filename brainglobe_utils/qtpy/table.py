from typing import Any, Optional

import pandas as pd
from qtpy.QtCore import QAbstractTableModel, QModelIndex, Qt


class DataFrameModel(QAbstractTableModel):
    """
    A Qt table model that wraps a pandas DataFrame for use with Qt
    view widgets.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to be displayed in the Qt view.

    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialize the model with a DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to be displayed.
        """
        super().__init__()
        self._df = df

    def rowCount(self, parent: Optional[QModelIndex] = None) -> int:
        """
        Return the number of rows in the model.

        Parameters
        ----------
        parent : Optional[QModelIndex], optional
            The parent index, by default None.

        Returns
        -------
        int
            The number of rows in the DataFrame.
        """
        return self._df.shape[0]

    def columnCount(self, parent: Optional[QModelIndex] = None) -> int:
        """
        Return the number of columns in the model.

        Parameters
        ----------
        parent : Optional[QModelIndex], optional
            The parent index, by default None.

        Returns
        -------
        int
            The number of columns in the DataFrame.
        """
        return self._df.shape[1]

    def data(
        self, index: QModelIndex, role: int = Qt.DisplayRole
    ) -> Optional[Any]:
        """
        Return the data at the given index for the specified role.

        Parameters
        ----------
        index : QModelIndex
            The index of the data to be retrieved.
        role : int, optional
            The role for which the data is being requested,
            by default Qt.DisplayRole.

        Returns
        -------
        Optional[Any]
            The data at the specified index, or None if the role
            is not Qt.DisplayRole.
        """
        if role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ) -> Optional[Any]:
        """
        Return the header data for the specified section and orientation.

        Parameters
        ----------
        section : int
            The section (column or row) for which the header data is requested.
        orientation : Qt.Orientation
            The orientation (horizontal or vertical) of the header.
        role : int, optional
            The role for which the header data is being requested, by
            default Qt.DisplayRole.

        Returns
        -------
        Optional[Any]
            The header data for the specified section and orientation, or
            None if the role is not Qt.DisplayRole.
        """

        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._df.columns[section]
            if orientation == Qt.Vertical:
                return self._df.index[section]
        return None
