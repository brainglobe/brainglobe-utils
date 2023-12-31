import os

import pandas as pd
import pytest
from natsort import natsorted

from brainglobe_utils.cells.cells import Cell
from brainglobe_utils.IO import cells as cell_io

data_dir = os.path.join("tests", "data")
xml_path = os.path.join(data_dir, "cells", "cells.xml")
yml_path = os.path.join(data_dir, "cells", "cells.yml")
cubes_dir = os.path.join(data_dir, "cube_extract", "cubes")
roi_sorter_output_dir = os.path.join(data_dir, "IO", "roi_sorter_output")

type_vals = [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
]
x_vals = [
    181,
    2117,
    4082,
    2137,
    2129,
    2141,
    2130,
    2130,
    2133,
    2141,
    2162,
    2127,
    1801,
    2176,
    2194,
    2664,
    2435,
    1266,
    568,
    2103,
    2098,
    2105,
    2208,
    2162,
    2221,
    2081,
    2230,
    2015,
    2072,
    1413,
    1950,
    3340,
    2051,
    3362,
    2046,
    2046,
    2046,
    2047,
    2032,
    2923,
    2064,
    2267,
    2297,
    2004,
    2356,
    2357,
    2359,
    2360,
    2365,
    2612,
    2623,
    2657,
    2906,
    2165,
    2685,
    2892,
    2896,
    2894,
    2901,
    2270,
    1924,
    2505,
    2531,
    2542,
    2536,
]
y_vals = [
    2379,
    133,
    332,
    134,
    133,
    134,
    132,
    133,
    136,
    136,
    130,
    1026,
    336,
    134,
    134,
    336,
    343,
    3427,
    2012,
    138,
    138,
    140,
    135,
    134,
    137,
    142,
    139,
    1045,
    141,
    2045,
    1048,
    142,
    142,
    145,
    150,
    151,
    151,
    151,
    146,
    147,
    147,
    147,
    1068,
    149,
    521,
    522,
    523,
    523,
    525,
    520,
    520,
    521,
    522,
    524,
    522,
    526,
    525,
    525,
    526,
    524,
    974,
    522,
    527,
    524,
    523,
]
z_vals = [
    1282,
    1276,
    1281,
    1286,
    1276,
    1278,
    1277,
    1278,
    1285,
    1297,
    1274,
    1294,
    1290,
    1279,
    1280,
    1296,
    1290,
    1294,
    1294,
    1285,
    1279,
    1289,
    1275,
    1286,
    1281,
    1284,
    1275,
    1291,
    1273,
    1294,
    1294,
    1274,
    1274,
    1274,
    1283,
    1287,
    1290,
    1294,
    1272,
    1275,
    1275,
    1274,
    1292,
    1273,
    1288,
    1286,
    1287,
    1289,
    1298,
    1274,
    1274,
    1273,
    1275,
    1275,
    1278,
    1286,
    1278,
    1288,
    1295,
    1279,
    1282,
    1275,
    1276,
    1275,
    1286,
]

cubes_cells = [
    Cell([340, 1004, 15], 1),
    Cell([340, 1004, 15], 1),
    Cell([392, 522, 10], 1),
    Cell([392, 522, 10], 1),
]

roi_sorter_cells = [
    Cell([4056, 564, 358], 1),
    Cell([3989, 267, 570], 1),
    Cell([4351, 735, 439], 1),
    Cell([4395, 677, 367], 1),
]


def test_get_cells():
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


def assert_cells_csv(csv_path):
    cells_df = pd.read_csv(csv_path)
    assert len(cells_df) == 65
    assert cells_df.type.tolist() == type_vals
    assert cells_df.x.tolist() == x_vals
    assert cells_df.y.tolist() == y_vals
    assert cells_df.z.tolist() == z_vals


def test_save_cells(tmp_path):
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.save_cells(cells, tmp_cells_out_path, save_csv=True)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))

    tmp_cells_out_path = tmp_path / "cells.csv"
    cell_io.cells_to_csv(cells, tmp_cells_out_path)
    assert_cells_csv(tmp_cells_out_path)


def test_cells_to_xml(tmp_path):
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.xml"
    cell_io.cells_to_xml(cells, tmp_cells_out_path)
    assert cells == cell_io.get_cells(str(tmp_cells_out_path))


def test_cells_xml_to_dataframe():
    cells_df = cell_io.cells_xml_to_df(xml_path)
    assert len(cells_df) == 65
    assert cells_df.type.tolist() == type_vals
    assert cells_df.x.tolist() == x_vals
    assert cells_df.y.tolist() == y_vals
    assert cells_df.z.tolist() == z_vals


def test_cells_to_csv(tmp_path):
    cells = cell_io.get_cells(xml_path)
    tmp_cells_out_path = tmp_path / "cells.csv"
    cell_io.cells_to_csv(cells, tmp_cells_out_path)
    assert_cells_csv(tmp_cells_out_path)
