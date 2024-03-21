import pandas as pd
import pytest
from natsort import natsorted

from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO import cells as cell_io


@pytest.fixture
def xml_path(data_path):
    return str(data_path / "cells" / "cells.xml")


@pytest.fixture
def yml_path(data_path):
    return str(data_path / "cells" / "cells.yml")


@pytest.fixture
def cubes_dir(data_path):
    return str(data_path / "cube_extract" / "cubes")


@pytest.fixture
def roi_sorter_output_dir(data_path):
    return str(data_path / "IO" / "roi_sorter_output")


@pytest.fixture
def type_vals():
    return [1] * 65


def read_csv_as_list(csv_path):
    df = pd.read_csv(csv_path, header=None)
    return df.to_numpy().flatten().tolist()


@pytest.fixture
def x_vals(data_path):
    csv_path = data_path / "IO" / "cell_io_vals" / "x_vals.csv"
    return read_csv_as_list(csv_path)


@pytest.fixture
def y_vals(data_path):
    csv_path = data_path / "IO" / "cell_io_vals" / "y_vals.csv"
    return read_csv_as_list(csv_path)


@pytest.fixture
def z_vals(data_path):
    csv_path = data_path / "IO" / "cell_io_vals" / "z_vals.csv"
    return read_csv_as_list(csv_path)


@pytest.fixture
def cubes_cells():
    return [
        Cell([340, 1004, 15], 1),
        Cell([340, 1004, 15], 1),
        Cell([392, 522, 10], 1),
        Cell([392, 522, 10], 1),
    ]


@pytest.fixture
def roi_sorter_cells():
    return [
        Cell([4056, 564, 358], 1),
        Cell([3989, 267, 570], 1),
        Cell([4351, 735, 439], 1),
        Cell([4395, 677, 367], 1),
    ]


def test_get_cells(
    cubes_cells,
    roi_sorter_cells,
    xml_path,
    yml_path,
    cubes_dir,
    roi_sorter_output_dir,
):
    cells = cell_io.get_cells(xml_path)
    assert len(cells) == 65
    assert Cell([2536, 523, 1286], 1) == cells[64]

    cells = cell_io.get_cells(yml_path)
    assert len(cells) == 250
    assert Cell([9170, 2537, 311], 1) == cells[194]

    cells = cell_io.get_cells(cubes_dir)
    assert len(cells) == 4
    assert natsorted(cubes_cells) == natsorted(cells)

    cells = cell_io.get_cells(roi_sorter_output_dir)
    assert len(cells) == 4
    assert natsorted(roi_sorter_cells) == natsorted(cells)

    with pytest.raises(NotImplementedError):
        assert cell_io.get_cells("misc_format.abc")


def assert_cells_csv(csv_path, x_vals, y_vals, z_vals, type_vals):
    cells_df = pd.read_csv(csv_path)
    assert len(cells_df) == 65
    assert cells_df.type.tolist() == type_vals
    assert cells_df.x.tolist() == x_vals
    assert cells_df.y.tolist() == y_vals
    assert cells_df.z.tolist() == z_vals


def test_save_cells(tmp_path, xml_path, x_vals, y_vals, z_vals, type_vals):
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.save_cells(cells, tmp_cells_out_path, save_csv=True)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))

    tmp_cells_out_path = tmp_path / "cells.csv"
    cell_io.cells_to_csv(cells, tmp_cells_out_path)
    assert_cells_csv(tmp_cells_out_path, x_vals, y_vals, z_vals, type_vals)


def test_cells_to_xml(tmp_path, xml_path):
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.cells_to_xml(cells, tmp_cells_out_path)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))


def test_cells_xml_to_dataframe(xml_path, x_vals, y_vals, z_vals, type_vals):
    cells_df = cell_io.cells_xml_to_df(xml_path)
    assert len(cells_df) == 65
    assert cells_df.type.tolist() == type_vals
    assert cells_df.x.tolist() == x_vals
    assert cells_df.y.tolist() == y_vals
    assert cells_df.z.tolist() == z_vals


def test_cells_to_csv(tmp_path, xml_path, x_vals, y_vals, z_vals, type_vals):
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.csv"
    cell_io.cells_to_csv(cells, tmp_cells_out_path)
    assert_cells_csv(tmp_cells_out_path, x_vals, y_vals, z_vals, type_vals)
