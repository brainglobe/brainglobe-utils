from anytree import AnyNode


class BrainStructure(AnyNode):
    def __init__(
        self, _id, name, _parent_structure_id, _structure_id_path,
    ):
        super(BrainStructure, self).__init__()
        self.id = _id
        self.name = name
        self._parent_structure_id = _parent_structure_id
        self._structure_id_path = _structure_id_path
