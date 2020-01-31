from imlib.anatomy.structures.structure import BrainStructure
from imlib.IO.structures import load_structures


class CellCountMissingCellsException(Exception):
    pass


class UnknownAtlasValue(Exception):
    pass


def atlas_value_to_structure_id(atlas_value, structures_reference_df):
    line = structures_reference_df[
        structures_reference_df["id"] == atlas_value
    ]
    if len(line) == 0:
        raise UnknownAtlasValue(atlas_value)
    structure_id = line["structure_id_path"].values[0]
    return structure_id


def atlas_value_to_name(atlas_value, structures_reference_df):
    line = structures_reference_df[
        structures_reference_df["id"] == atlas_value
    ]
    if len(line) == 0:
        raise UnknownAtlasValue(atlas_value)
    name = line["name"]
    return str(name.values[0])


class StructureNotFoundError(Exception):
    def __init__(self, _id):
        self._id = _id

    def __str__(self):
        return "Missing structure with id {}".format(self._id)


def get_struct_by_id(structures, _id):
    for struct in structures:
        if struct.id == _id:
            return struct
    raise StructureNotFoundError(_id)


def get_structures_tree(structures_file_path):
    header, structures_data = load_structures(structures_file_path)
    structures = []
    for struct_data in structures_data:
        struct = BrainStructure(*struct_data)
        if structures:
            struct.parent = get_struct_by_id(
                structures, struct._parent_structure_id
            )
        structures.append(struct)
    return structures
