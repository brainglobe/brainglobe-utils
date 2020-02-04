import pytest
from pathlib import Path

from imlib.IO.structures import load_structures_as_df
from imlib.anatomy.structures import structures_tree

data_dir = Path("tests", "data")
structures_csv = data_dir / "structures" / "structures.csv"

structure_id_100 = "/997/8/343/313/348/165/100/"


def test_atlas_value_to_structure_id():
    structure_df = load_structures_as_df(structures_csv)
    assert structure_id_100 == structures_tree.atlas_value_to_structure_id(
        100, structure_df
    )

    with pytest.raises(structures_tree.UnknownAtlasValue):
        structures_tree.atlas_value_to_structure_id(100000, structure_df)


def test_atlas_value_to_name():
    structure_df = load_structures_as_df(structures_csv)
    assert "Interpeduncular nucleus" == structures_tree.atlas_value_to_name(
        100, structure_df
    )

    with pytest.raises(structures_tree.UnknownAtlasValue):
        structures_tree.atlas_value_to_name(100000, structure_df)
