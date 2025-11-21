import os
from pathlib import Path
from xml.etree import ElementTree

import pandas as pd
import pytest
import yaml
from natsort import natsorted

from brainglobe_utils.cells.cells import Cell, UntypedCell, pos_from_file_name
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


@pytest.mark.parametrize("suffix", [".yml", ".xml"])
def test_get_cells(xml_path, yml_path, suffix):
    """
    Test that cells can be read from an XML/YAML file.
    """
    path = xml_path if suffix == ".xml" else yml_path
    cells = cell_io.get_cells(path)
    assert len(cells) == 65
    assert Cell([2536, 523, 1286], 1) == cells[64]

    if suffix == ".yml":
        assert Cell([181, 2379, 1282], 1, {"hello": "cells"}) == cells[0]
    else:
        assert Cell([181, 2379, 1282], 1) == cells[0]


def check_artifacts_get(cells_only, cells, cells_with_artifacts):
    if cells_only:
        assert len(cells) == 2
        for cell in cells:
            assert cell.type == 2
    else:
        assert len(cells) == len(cells_with_artifacts)


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
    check_artifacts_get(cells_only, cells, cells_with_artifacts)


@pytest.mark.parametrize("cells_only", [True, False])
def test_get_cells_yaml_cells_only(cells_only, tmp_path, cells_with_artifacts):
    """
    Test that cells not of type Cell.CELL (type 2) are correctly removed or
    kept when reading from xml with the cells_only option.
    """
    tmp_cells_out_path = tmp_path / "cells.yml"
    cell_io.cells_to_yml(
        cells_with_artifacts, tmp_cells_out_path, artifact_keep=True
    )
    cells = cell_io.get_cells(str(tmp_cells_out_path), cells_only=cells_only)
    check_artifacts_get(cells_only, cells, cells_with_artifacts)


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


@pytest.mark.parametrize("suffix", [".yml", ".xml"])
def test_empty_files(tmp_path, suffix):
    """Check bad files raise error."""
    empty_file = tmp_path / f"data{suffix}"

    with open(empty_file, "w") as fh:
        if suffix == ".yml":
            yaml.dump({}, fh)

    with pytest.raises((NotImplementedError, ElementTree.ParseError)):
        # raise for unknown file format
        assert cell_io.get_cells(empty_file)


@pytest.mark.parametrize("suffix", [".yml", ".xml"])
def test_save_cells(tmp_path, xml_path, yml_path, suffix):
    """
    Test that cells can be written to a csv file via the save_csv option of
    cell_io.save_cells.
    """
    path = xml_path if suffix == ".xml" else yml_path
    cells = cell_io.get_cells(path)
    tmp_cells_out_path = tmp_path / f"cells{suffix}"
    cell_io.save_cells(cells, tmp_cells_out_path, save_csv=True)
    assert cells == cell_io.get_cells(tmp_cells_out_path)


def test_cells_to_xml(tmp_path, xml_path):
    """
    Test that cells can be written to an xml file.
    """
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.cells_to_xml(cells, tmp_cells_out_path)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))


def test_cells_to_yml(tmp_path, yml_path):
    """
    Test that cells can be written to an xml file.
    """
    cells = cell_io.get_cells(yml_path)
    tmp_cells_out_path = tmp_path / "cells.yml"
    cell_io.cells_to_yml(cells, tmp_cells_out_path)
    assert cells == cell_io.get_cells(tmp_cells_out_path)


def check_artifact_save(artifact_keep, written_cells, cells_with_artifacts):
    if artifact_keep:
        # Check that artifact cells (type -1) have been kept, and their
        # type changed to 1
        assert len(written_cells) == len(cells_with_artifacts)
        for i, cell in enumerate(cells_with_artifacts):
            if cell.type == -1:
                assert written_cells[i].type == Cell.UNKNOWN
            else:
                assert written_cells[i].type == cell.type
    else:
        # Check artifact cells (type -1) have been removed
        assert len(written_cells) == 3
        assert written_cells == cells_with_artifacts[2:]


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
    written_cells = cell_io.get_cells(tmp_cells_out_path)
    check_artifact_save(artifact_keep, written_cells, cells_with_artifacts)


@pytest.mark.parametrize("artifact_keep", [True, False])
def test_cells_to_yml_artifacts_keep(
    cells_with_artifacts, tmp_path, artifact_keep
):
    """
    Test that artifact cells (type -1) are correctly removed or kept when
    writing to xml with the artifact_keep option.
    """
    tmp_cells_out_path = tmp_path / "cells.yml"
    cell_io.cells_to_yml(
        cells_with_artifacts, tmp_cells_out_path, artifact_keep=artifact_keep
    )
    written_cells = cell_io.get_cells(tmp_cells_out_path)
    check_artifact_save(artifact_keep, written_cells, cells_with_artifacts)


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


@pytest.mark.parametrize(
    "cell_def_path", ["", "cells.xml"], ids=["directory", "xml"]
)
def test_find_relevant_tiffs(data_path, tmp_path, cell_def_path):
    """
    Test that tiff paths can be selected that match cells from an xml file
    or directory.
    """
    tiff_dir = data_path / "cube_extract" / "cubes"

    # Write a cell_def xml file or directory that only contains 1 of the
    # cells from tiff_dir
    cell_def_path = tmp_path / cell_def_path
    chosen_tiff = os.listdir(tiff_dir)[0]
    cell = UntypedCell(chosen_tiff)
    if cell_def_path.suffix == ".xml":
        cell_io.cells_to_xml([cell], cell_def_path)
    else:
        cell_path = cell_def_path / f"x{cell.x}_y{cell.y}_z{cell.z}.tif"
        cell_path.touch()

    selected = cell_io.find_relevant_tiffs(
        os.listdir(tiff_dir), str(cell_def_path)
    )
    for selected_path in selected:
        assert pos_from_file_name(selected_path) == pos_from_file_name(
            chosen_tiff
        )


def test_xml_to_yaml(xml_path, tmp_path):
    # load xml, dump to yaml and load again and compare
    yml_path: Path = tmp_path / "cells.yaml"

    xml_cells_in = cell_io.get_cells(xml_path)
    assert xml_cells_in

    assert not yml_path.exists()
    cell_io.save_cells(xml_cells_in, yml_path)
    assert yml_path.exists()

    yml_cells_in = cell_io.get_cells(yml_path)
    assert len(xml_cells_in) == len(yml_cells_in)
    assert yml_cells_in == xml_cells_in

    # change one cell and make sure it's different now
    xml_cells_in[0].x += 1
    assert yml_cells_in != xml_cells_in


def test_yaml_xml_metadata(tmp_path):
    """Check that yaml saves metadata but not xml."""
    yml_path: Path = tmp_path / "cells.yaml"
    xml_path: Path = tmp_path / "cells.xml"
    cells = [
        Cell((1, 2, 3), Cell.UNKNOWN, metadata={}),
        Cell((11, 12, 13), Cell.UNKNOWN, metadata={"1": 2}),
        Cell((21, 22, 23), Cell.CELL, metadata={"3": 5}),
        Cell((31, 32, 33), Cell.UNKNOWN, metadata={"hello": True}),
    ]

    cell_io.save_cells(cells, xml_path)
    cell_io.save_cells(cells, yml_path)
    xml_cells = cell_io.get_cells(xml_path, cells_only=False)
    yml_cells = cell_io.get_cells(yml_path, cells_only=False)

    # same num of cells
    assert len(xml_cells) == 4
    assert len(yml_cells) == 4

    # yaml cells are same, not xml because it doesn't have metadata
    assert set(yml_cells) == set(cells)
    assert set(xml_cells) != set(cells)

    # clear metadata and now it should be same as xml
    for cell in cells:
        cell.metadata = {}
    assert set(xml_cells) == set(cells)


@pytest.mark.parametrize("suffix", [".yml", ".xml"])
def test_is_brainglobe_xml(tmp_path, suffix):
    valid = tmp_path / f"valid{suffix}"
    invalid = tmp_path / f"invalid{suffix}"
    no_exists = tmp_path / f"not_exists{suffix}"

    f = (
        cell_io.is_brainglobe_xml
        if suffix == ".xml"
        else cell_io.is_brainglobe_yaml
    )

    cells = [Cell((1, 2, 3), Cell.CELL)]
    cell_io.save_cells(cells, valid)
    assert f(valid)

    invalid.write_text("hello")
    assert not f(invalid)
    assert not f(no_exists)


@pytest.mark.parametrize("suffix", [".yml", ".xml"])
def test_no_cells(tmp_path, suffix):
    fname = tmp_path / f"cells{suffix}"

    cell_io.save_cells([], fname)
    with pytest.raises(cell_io.MissingCellsError):
        cell_io.get_cells(fname)
