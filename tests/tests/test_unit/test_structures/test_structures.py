import pytest
from pathlib import Path
from pandas import Index
from numpy import nan

from imlib.IO.structures import load_structures_as_df, load_structures
from imlib.anatomy.structures.structure import BrainStructure
from imlib.anatomy.structures import structures_tree

data_dir = Path("tests", "data")
structures_csv = data_dir / "structures" / "structures.csv"


brain_structure_100 = BrainStructure(
    "378",
    "Supplemental somatosensory area",
    "453",
    "/997/8/567/688/695/315/453/378/",
)

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


def test_structure_not_found_error():
    structures_tree_list = structures_tree.get_structures_tree(structures_csv)
    with pytest.raises(structures_tree.StructureNotFoundError):
        structures_tree.get_struct_by_id(structures_tree_list, "1000000")

    assert (
        str(structures_tree.StructureNotFoundError("342"))
        == "Missing structure with id 342"
    )


def test_get_structure_by_id():
    structures_tree_list = structures_tree.get_structures_tree(structures_csv)
    structure = structures_tree.get_struct_by_id(structures_tree_list, "378")
    assert structure.name == "Supplemental somatosensory area"

    with pytest.raises(structures_tree.StructureNotFoundError):
        structures_tree.get_struct_by_id(structures_tree_list, "1000000")


def test_get_structures_tree_and_brain():
    structures_tree_list = structures_tree.get_structures_tree(structures_csv)
    assert len(structures_tree_list) == 1299
    assert brain_structure_100.name == structures_tree_list[100].name
    assert brain_structure_100.id == structures_tree_list[100].id
