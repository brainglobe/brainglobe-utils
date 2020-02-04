from pathlib import Path
from pandas import Index

from imlib.IO.structures import load_structures_as_df

data_dir = Path("tests", "data")
structures_csv = data_dir / "structures" / "structures.csv"

structure_headers = [
    "id",
    "name",
    "parent_structure_id",
    "structure_id_path",
]

structures_line_100 = [
    378,
    "Supplemental somatosensory area",
    453.0,
    "/997/8/567/688/695/315/453/378/",
]


def test_load_structures_df():
    structures = load_structures_as_df(structures_csv)

    assert len(structures) == 1299
    assert (structures.keys() == Index(structure_headers)).all()

    structures_test = list(structures.iloc[100].array)

    assert structures_test[1] == structures_line_100[1]
    assert structures_test[2] == structures_line_100[2]
    assert structures_test[3] == structures_line_100[3]
