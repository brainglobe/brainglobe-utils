from pathlib import Path

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
def cells_with_artifacts():
    return [
        Cell([340, 1004, 15], -1),
        Cell([340, 1004, 15], -1),
        Cell([392, 522, 10], 1),
        Cell([392, 522, 10], 2),
        Cell([392, 522, 10], 2),
    ]


def test_get_cells_xml(xml_path):
    """
    Test that cells can be read from an xml file.
    """
    cells = cell_io.get_cells(xml_path)
    assert len(cells) == 65
    assert Cell([2536, 523, 1286], 1) == cells[64]


@pytest.mark.parametrize("cells_only", [True, False])
def test_get_cells_xml_cells_only(cells_only, tmp_path, cells_with_artifacts):
    """
    Test that cells not of type Cell.CELL (type 2) are correctly removed or
    kept when reading from xml with the cells_only option.
    """
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.cells_to_xml(
        cells_with_artifacts, tmp_cells_out_path, artifact_keep=True
    )
    cells = cell_io.get_cells(str(tmp_cells_out_path), cells_only=cells_only)

    if cells_only:
        assert len(cells) == 2
        for cell in cells:
            assert cell.type == 2
    else:
        assert len(cells) == len(cells_with_artifacts)


def test_get_cells_yml(yml_path):
    """
    Test that cells can be read from a yml file.
    """
    cells = cell_io.get_cells(yml_path)
    assert len(cells) == 250
    assert Cell([9170, 2537, 311], 1) == cells[194]


@pytest.mark.parametrize(
    "cells_dir, expected_cells",
    [
        (
            Path("cube_extract") / "cubes",
            [
                Cell([340, 1004, 15], 1),
                Cell([340, 1004, 15], 1),
                Cell([392, 522, 10], 1),
                Cell([392, 522, 10], 1),
            ],
        ),
        (
            Path("IO") / "roi_sorter_output",
            [
                Cell([4056, 564, 358], 1),
                Cell([3989, 267, 570], 1),
                Cell([4351, 735, 439], 1),
                Cell([4395, 677, 367], 1),
            ],
        ),
    ],
)
def test_get_cells_dir(data_path, cells_dir, expected_cells):
    """
    Test that cells can be read from a directory.
    """
    cells = cell_io.get_cells(str(data_path / cells_dir))
    assert len(cells) == 4
    assert natsorted(cells) == natsorted(expected_cells)


def test_get_cells_error(tmp_path):
    """
    Test that get_cells throws an error for unknown file formats, and
    directories containing files that can't be read.
    """
    unknown_file = tmp_path / "misc_format.abc"
    unknown_file.touch()

    with pytest.raises(NotImplementedError):
        # raise for unknown file format
        assert cell_io.get_cells(str(unknown_file))

    with pytest.raises(NotImplementedError):
        # raise for directory with files that can't be read
        cell_io.get_cells(str(tmp_path))


def test_save_cells(tmp_path, xml_path, x_vals, y_vals, z_vals, type_vals):
    """
    Test that cells can be written to a csv file via the save_csv option of
    cell_io.save_cells.
    """
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.save_cells(cells, tmp_cells_out_path, save_csv=True)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))


def test_cells_to_xml(tmp_path, xml_path):
    """
    Test that cells can be written to an xml file.
    """
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.cells_to_xml(cells, tmp_cells_out_path)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))


@pytest.mark.parametrize("artifact_keep", [True, False])
def test_cells_to_xml_artifacts_keep(
    cells_with_artifacts, tmp_path, artifact_keep
):
    """
    Test that artifact cells (type -1) are correctly removed or kept when
    writing to xml with the artifact_keep option.
    """
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.cells_to_xml(
        cells_with_artifacts, tmp_cells_out_path, artifact_keep=artifact_keep
    )
    written_cells = cell_io.get_cells(str(tmp_cells_out_path))

    if artifact_keep:
        # Check that artifact cells (type -1) have been kept, and their
        # type changed to 1
        assert len(written_cells) == len(cells_with_artifacts)
        for i, cell in enumerate(cells_with_artifacts):
            if cell.type == -1:
                assert written_cells[i] == 1
            else:
                assert written_cells[i].type == cell.type
    else:
        # Check artifact cells (type -1) have been removed
        assert len(written_cells) == 3
        assert written_cells == cells_with_artifacts[2:]


def assert_cells_df(cells_df, x_vals, y_vals, z_vals, type_vals):
    """
    Check that there are the correct number of cells in the Dataframe, and
    that each has the correct type and position.
    """
    assert len(cells_df) == 65
    assert cells_df.type.tolist() == type_vals
    assert cells_df.x.tolist() == x_vals
    assert cells_df.y.tolist() == y_vals
    assert cells_df.z.tolist() == z_vals


def test_cells_xml_to_dataframe(xml_path, x_vals, y_vals, z_vals, type_vals):
    """
    Test that cells can be read from an xml file, and correctly converted
    into a DataFrame.
    """
    cells_df = cell_io.cells_xml_to_df(xml_path)
    assert_cells_df(cells_df, x_vals, y_vals, z_vals, type_vals)


def test_cells_to_csv(tmp_path, xml_path, x_vals, y_vals, z_vals, type_vals):
    """
    Test that cells can be written to a csv file.
    """
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.csv"
    cell_io.cells_to_csv(cells, tmp_cells_out_path)
    cells_df = pd.read_csv(tmp_cells_out_path)
    assert_cells_df(cells_df, x_vals, y_vals, z_vals, type_vals)
