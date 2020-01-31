from pathlib import Path
from pandas import Index
from numpy import nan, isnan

from imlib.IO.structures import load_structures_as_df, load_structures

data_dir = Path("tests", "data")
structures_csv = data_dir / "structures" / "structures.csv"

structure_headers = [
    "id",
    "atlas_id",
    "name",
    "acronym",
    "st_level",
    "ontology_id",
    "hemisphere_id",
    "weight",
    "parent_structure_id",
    "depth",
    "graph_id",
    "graph_order",
    "structure_id_path",
    "color_hex_triplet",
    "neuro_name_structure_id",
    "neuro_name_structure_id_path",
    "failed",
    "sphinx_id",
    "structure_name_facet",
    "failed_facet",
    "safe_name",
]

structures_line_100 = [
    378,
    754.0,
    "Supplemental somatosensory area",
    "SSs",
    nan,
    1,
    3,
    8690,
    453.0,
    7,
    1,
    100,
    "/997/8/567/688/695/315/453/378/",
    "188064",
    nan,
    nan,
    "f",
    101,
    713142416,
    734881840,
    "Supplemental somatosensory area",
]


structures_line_100_strings = [
    "378",
    "754",
    "Supplemental somatosensory area",
    "SSs",
    "",
    "1",
    "3",
    "8690",
    "453",
    "7",
    "1",
    "100",
    "/997/8/567/688/695/315/453/378/",
    "188064",
    "",
    "",
    "f",
    "101",
    "713142416",
    "734881840",
    "Supplemental somatosensory area",
]


def test_load_structures():
    structures = load_structures(structures_csv)

    assert len(structures[0]) == 21
    assert len(structures[1]) == 1299

    assert structures[0] == structure_headers
    assert structures[1][100] == structures_line_100_strings


def test_load_structures_df():
    structures = load_structures_as_df(structures_csv)

    assert len(structures) == 1299
    assert (structures.keys() == Index(structure_headers)).all()

    structures_test = list(structures.iloc[100].array)

    assert structures_test[1] == structures_line_100[1]
    assert structures_test[2] == structures_line_100[2]
    assert structures_test[3] == structures_line_100[3]
    assert structures_test[10] == structures_line_100[10]
    assert structures_test[11] == structures_line_100[11]
    assert structures_test[12] == structures_line_100[12]
    assert structures_test[20] == structures_line_100[20]
