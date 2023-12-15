"""
Based on https://github.com/SainsburyWellcomeCentre/niftynet_cell_count by
Christian Niedworok (https://github.com/cniedwor).
"""
import math
import os
import re
from collections import defaultdict
from functools import total_ordering
from typing import Any, DefaultDict, Dict, List, Tuple, Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as EtElement


@total_ordering
class Cell:
    ARTIFACT = -1
    CELL = 2
    UNKNOWN = 1

    # for classification compatibility
    NO_CELL = 1

    def __init__(
        self,
        pos: Union[str, ElementTree.Element, Dict[str, float], List[float]],
        cell_type: int,
    ):
        if isinstance(pos, str):
            pos = pos_from_file_name(os.path.basename(pos))
        if isinstance(pos, ElementTree.Element):
            pos = pos_from_xml_marker(pos)
        if isinstance(pos, dict):
            pos = pos_from_dict(pos)
        pos = self._sanitize_position(pos)
        x, y, z = [int(p) for p in pos]
        self.x: float = x
        self.y: float = y
        self.z: float = z

        self.transformed_x: float = x
        self.transformed_y: float = y
        self.transformed_z: float = z

        self.structure_id = None
        self.hemisphere = None

        self.type: int
        if cell_type is None:
            self.type = Cell.UNKNOWN
        elif str(cell_type).lower() == "cell":
            self.type = Cell.CELL
        elif str(cell_type).lower() == "no_cell":
            self.type = Cell.ARTIFACT
        else:
            self.type = int(cell_type)

    def _sanitize_position(
        self, pos: List[float], verbose: bool = True
    ) -> List[float]:
        out = []
        for coord in pos:
            if math.isnan(coord):
                if verbose:
                    print(
                        "WARNING: NaN position for for cell\n"
                        "defaulting to 1"
                    )
                coord = 1
            out.append(coord)
        return out

    def _transform(
        self,
        x_scale: float = 1.0,
        y_scale: float = 1.0,
        z_scale: float = 1.0,
        x_offset: float = 0,
        y_offset: float = 0,
        z_offset: float = 0,
        integer: bool = False,
    ) -> Tuple[float, float, float]:
        x = self.x
        y = self.y
        z = self.z

        x += x_offset
        y += y_offset
        z += z_offset

        x *= x_scale
        y *= y_scale
        z *= z_scale

        if integer:
            return int(round(x)), int(round(y)), int(round(z))
        else:
            return x, y, z

    def transform(
        self,
        x_scale: float = 1.0,
        y_scale: float = 1.0,
        z_scale: float = 1.0,
        x_offset: float = 0,
        y_offset: float = 0,
        z_offset: float = 0,
        integer: bool = False,
    ) -> None:
        transformed_coords = self._transform(
            x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer
        )
        self.x, self.y, self.z = transformed_coords

    def soft_transform(
        self,
        x_scale: float = 1.0,
        y_scale: float = 1.0,
        z_scale: float = 1.0,
        x_offset: float = 0,
        y_offset: float = 0,
        z_offset: float = 0,
        integer: bool = False,
    ) -> None:
        transformed_coords = self._transform(
            x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer
        )
        (
            self.transformed_x,
            self.transformed_y,
            self.transformed_z,
        ) = transformed_coords

    def flip_x_y(self) -> None:
        self.y, self.x = self.x, self.y

    def is_cell(self) -> bool:
        return self.type == Cell.CELL

    def to_xml_element(self) -> EtElement:
        sub_elements = [EtElement("Marker{}".format(axis)) for axis in "XYZ"]
        coords = [int(coord) for coord in (self.x, self.y, self.z)]
        for sub_element, coord in zip(sub_elements, coords):
            if coord < 1:
                print(
                    "WARNING: negative coordinate found at {}\n"
                    "defaulting to 1".format(coord)
                )
                coord = 1  # FIXME:
            sub_element.text = str(coord)

        element = EtElement("Marker")
        element.extend(sub_elements)
        return element

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return (self.x, self.y, self.z, self.type) == (
            other.x,
            other.y,
            other.z,
            other.type,
        )

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __lt__(self, other: Any) -> Union[bool, NotImplementedError]:
        if self == other:
            return False
        try:
            if self.z < other.z:
                return True
            elif self.z > other.z:
                return False
            elif self.y < other.y:
                return True
            elif self.y > other.y:
                return False
            elif self.x < other.x:
                return True
            else:
                return False
        except AttributeError as err:
            return NotImplementedError(
                "comparison to {} is not implemented, {}".format(
                    type(other), err
                )
            )

    def __str__(self) -> str:
        return "Cell: x: {}, y: {}, z: {}, type: {}".format(
            int(self.x), int(self.y), int(self.z), self.type
        )

    def __repr__(self) -> str:
        return "{}, ({}, {})".format(
            self.__class__, [self.x, self.y, self.z], self.type
        )

    def to_dict(self) -> Dict[str, float]:
        return {"x": self.x, "y": self.y, "z": self.z, "type": self.type}

    def __hash__(self) -> int:
        return hash(str(self))


class UntypedCell(Cell):
    def __init__(
        self,
        pos: Union[str, ElementTree.Element, Dict[str, float], List[float]],
    ) -> None:
        super(UntypedCell, self).__init__(pos, self.UNKNOWN)

    @property
    def type(self) -> int:
        return self.UNKNOWN

    @type.setter
    def type(self, value: int) -> None:
        pass

    @classmethod
    def from_cell(cls, cell: Cell) -> "UntypedCell":
        return cls([cell.x, cell.y, cell.z])

    def to_cell(self) -> Cell:
        return Cell([self.x, self.y, self.z], self.type)


def pos_from_dict(position_dict: Dict[str, float]) -> List[float]:
    return [position_dict["x"], position_dict["y"], position_dict["z"]]


def pos_from_xml_marker(element: ElementTree.Element) -> List[float]:
    marker_names = ["Marker{}".format(axis) for axis in "XYZ"]
    markers = [element.find(marker_name) for marker_name in marker_names]
    pos = [marker.text for marker in markers if marker is not None]
    return [float(num) for num in pos if num is not None]


def pos_from_file_name(file_name: str) -> List[float]:
    x = re.findall(r"x\d+", file_name.lower())
    y = re.findall(r"y\d+", file_name.lower())
    z = re.findall(r"z\d+", file_name.lower())
    return [int(p) for p in (x[-1][1:], y[-1][1:], z[-1][1:])]


def group_cells_by_z(cells: List[Cell]) -> DefaultDict[float, List[Cell]]:
    """
    For a list of Cells return a dict of lists of cells, grouped by plane.

    :param list cells: list of cells from cellfinder.cells.cells.Cell
    :return:  defaultdict, with each key being a plane (e.g. 1280)
    and each entry being a list of Cells
    """
    cells_groups = defaultdict(list)
    for cell in cells:
        cells_groups[cell.z].append(cell)
    return cells_groups


class MissingCellsError(Exception):
    pass
