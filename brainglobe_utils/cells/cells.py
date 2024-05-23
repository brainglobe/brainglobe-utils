"""
Based on https://github.com/SainsburyWellcomeCentre/niftynet_cell_count by
Christian Niedworok (https://github.com/cniedwor).
"""

import math
import os
import re
import threading
from collections import defaultdict
from functools import total_ordering
from typing import (
    Any,
    DefaultDict,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
)
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as EtElement

import numpy as np
from numba import njit, objmode
from tqdm import tqdm


@total_ordering
class Cell:
    """
    A class representing a cell with a specific type.

    Parameters
    ----------
    pos : str or ElementTree.Element or Dict[str, float] or List of float
        Cell position (x, y, z). Input can be a filename containing the x/y/z
        position, an xml marker element, a dictionary with keys "x", "y" and
        "z", or a list of the positions [x, y, z].

    cell_type : int or str or None
        Cell type represented by an integer: 1 for unknown/no cell,
        2 for cell, -1 for artifact. The usual way to set this is to use:
        Cell.ARTIFACT, Cell.CELL, Cell.UNKNOWN, or Cell.NO_CELL as input.
        You can also pass "cell" or "no_cell", as well as None (which will
        map to Cell.UNKNOWN).

    Attributes
    ----------
    x : float
        X position.

    y : float
        Y position.

    z : float
        Z position.

    type : int
        Cell type. 1 for unknown/no cell, 2 for cell, -1 for artifact.

    transformed_x : float
        Transformed x position.

    transformed_y : float
        Transformed y position.

    transformed_z : float
        Transformed z position.

    structure_id : int
        ID of brain structure.

    hemisphere : str
        Hemisphere of brain.
    """

    # integers for self.type
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
        """
        Scale and/or offset the cell position. .x / .y / .z will be updated.

        Parameters
        ----------
        x_scale : float
            Value to scale the x coordinate by.

        y_scale : float
            Value to scale the y coordinate by.

        z_scale : float
            Value to scale the z coordinate by.

        x_offset : float
            Distance to offset in x.

        y_offset : float
            Distance to offset in y.

        z_offset : float
            Distance to offset in z.

        integer : bool
            Whether to round xyz position to nearest integer.
        """
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
        """
        Scale and/or offset the cell position. New values will be saved into
        .transformed_x, .transformed_y and .transformed_z. Original .x, .y and
        .z will remain unchanged.

        See Also
        --------
        Cell.transform : For description of parameters.
        """
        transformed_coords = self._transform(
            x_scale, y_scale, z_scale, x_offset, y_offset, z_offset, integer
        )
        (
            self.transformed_x,
            self.transformed_y,
            self.transformed_z,
        ) = transformed_coords

    def flip_x_y(self) -> None:
        """Swap the x and y coordinate"""
        self.y, self.x = self.x, self.y

    def is_cell(self) -> bool:
        return self.type == Cell.CELL

    def to_xml_element(self) -> EtElement:
        """
        Create an xml element representing the cell, including its xyz
        coordinate.
        """
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
        """Return true if position and type of the cells are equal"""
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
    """
    A class representing a cell with no type.

    Parameters
    ----------
    pos : str or ElementTree.Element or Dict[str, float] or List of float
        Cell position (x, y, z). Input can be a filename containing the x/y/z
        position, an xml marker element, a dictionary with keys "x", "y" and
        "z", or a list of the positions [x, y, z].

    See Also
    --------
    Cell : For description of attributes.
    """

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
    """Return [x, y, z] position from dictionary with keys of x, y and z"""
    return [position_dict["x"], position_dict["y"], position_dict["z"]]


def pos_from_xml_marker(element: ElementTree.Element) -> List[float]:
    """Return [x, y, z] position from xml marker"""
    marker_names = ["Marker{}".format(axis) for axis in "XYZ"]
    markers = [element.find(marker_name) for marker_name in marker_names]
    pos = [marker.text for marker in markers if marker is not None]
    return [float(num) for num in pos if num is not None]


def pos_from_file_name(file_name: str) -> List[float]:
    """Return [x, y, z] position from filename. For example,
    'pCellz10y522x392Ch0.tif' would return [392, 522, 10]"""
    x = re.findall(r"x\d+", file_name.lower())
    y = re.findall(r"y\d+", file_name.lower())
    z = re.findall(r"z\d+", file_name.lower())
    return [int(p) for p in (x[-1][1:], y[-1][1:], z[-1][1:])]


def group_cells_by_z(cells: List[Cell]) -> DefaultDict[float, List[Cell]]:
    """
    For a list of Cells return a dict of lists of cells, grouped by plane.

    Parameters
    ----------
    cells : List of Cell
        List of cells from brainglobe_utils.cells.cells.Cell

    Returns
    -------
    DefaultDict
        defaultdict, with each key being a plane (e.g. 1280) and each entry
        being a list of Cells
    """
    cells_groups = defaultdict(list)
    for cell in cells:
        cells_groups[cell.z].append(cell)
    return cells_groups


class MissingCellsError(Exception):
    """Custom exception class for when no cells are found in a file"""

    pass


def to_numpy_pos(
    cells: List[Cell], cell_type: Optional[int] = None
) -> np.ndarray:
    """
    Takes a list of Cell objects, selects only cells of type `cell_type` (if
    not None) and returns a single 2d array of shape Nx3 with the
    positions of the cells.
    """
    # for large cell list, pre-compute size
    n = len(cells)
    if cell_type is not None:
        n = sum([cell.type == cell_type for cell in cells])
    np_cells = np.empty((n, 3), dtype=np.float_)

    i = 0
    for cell in cells:
        if cell_type is not None and cell.type != cell_type:
            continue
        np_cells[i, :] = cell.x, cell.y, cell.z
        i += 1

    return np_cells


def from_numpy_pos(pos: np.ndarray, cell_type: int) -> List[Cell]:
    """
    Takes a 2d numpy position array of shape Nx3 and returns a list of Cell
    objects of given cell_type from those positions.
    """
    cells = []
    for i in range(pos.shape[0]):
        cell = Cell(pos=pos[i, :].tolist(), cell_type=cell_type)
        cells.append(cell)

    return cells


def match_cells(
    cells: List[Cell], other: List[Cell], threshold: float = np.inf
) -> Tuple[List[int], List[Tuple[int, int]], List[int]]:
    """
    Given two lists of cells. It finds a pairing of cells from `cells` and
    `other` such that the distance (euclidian) between the assigned matches
    across all `cells` is minimized.

    Remaining cells (e.g. if one list is longer or if there are matches
    violating the threshold) are indicated as well.

    E.g.::

        >>> cells = [
        >>>     Cell([20, 20, 20], Cell.UNKNOWN),
        >>>     Cell([10, 10, 10], Cell.UNKNOWN),
        >>>     Cell([40, 40, 40], Cell.UNKNOWN),
        >>>     Cell([50, 50, 50], Cell.UNKNOWN),
        >>> ]
        >>> other = [
        >>>     Cell([5, 5, 5], Cell.UNKNOWN),
        >>>     Cell([15, 15, 15], Cell.UNKNOWN),
        >>>     Cell([35, 35, 35], Cell.UNKNOWN),
        >>>     Cell([100, 100, 100], Cell.UNKNOWN),
        >>>     Cell([200, 200, 200], Cell.UNKNOWN),
        >>> ]
        >>> match_cells(cells, other, threshold=20)
        ([3], [[0, 1], [1, 0], [2, 2]], [3, 4])

    Parameters
    ----------
    cells : list of Cells.
    other : Another list of Cells.
    threshold : float, optional. Defaults to np.inf.
        The threshold to use to remove bad matches. Any match pair whose
        distance is greater than the threshold will be exluded from the
        matching.

    Returns
    -------
    tuple :
        missing_cells: List of all the indices of `cells` that found no match
            in `other` (sorted).
        good_matches: List of tuples with all the (cells, other) indices pairs
            that matched below the threshold. It's sorted by the `cells`
            column.
        missing_other: List of all the indices of `other` that found no match
            in `cells` (sorted).
    """
    if __progress_update.updater is not None:
        # I can't think of an instance where this will happen, but better safe
        raise TypeError(
            "An instance of match_cells is already running in this "
            "thread. Try running again once it completes"
        )
    c1 = to_numpy_pos(cells)
    c2 = to_numpy_pos(other)

    # c1 must be smaller or equal in length than c2
    flip = len(cells) > len(other)
    if flip:
        c1, c2 = c2, c1

    progress = tqdm(desc="Matching cells", total=len(c1), unit="cells")
    __progress_update.updater = progress.update
    # for each index corresponding to c1, returns the index in c2 that matches
    try:
        assignment = match_points(c1, c2, threshold)
        progress.close()
    finally:
        __progress_update.updater = None

    missing_c1, good_matches, missing_c2 = analyze_point_matches(
        c1, c2, assignment, threshold
    )
    if flip:
        missing_c1, missing_c2 = missing_c2, missing_c1
        good_matches = np.flip(good_matches, axis=1)
        good_matches = good_matches[good_matches[:, 0].argsort()]

    return missing_c1.tolist(), good_matches.tolist(), missing_c2.tolist()


# terrible hack. But you can't pass arbitrary objects to a njit function. But,
# it can access global variables and run them in objmode. So pass the progress
# updater to match_points via this global variable and function. We make it
# thread safe nominally, but it's not safe to modify within a thread while
# match_points is running

__progress_update = threading.local()
__progress_update.updater = None


def __compare_progress():
    if __progress_update.updater is not None:
        __progress_update.updater()


@njit
def match_points(
    pos1: np.ndarray, pos2: np.ndarray, threshold: float = np.inf
) -> np.ndarray:
    """
    Given two arrays, each a list of position. For each point in `pos1` it
    finds a point in `pos2` such that the distance between the assigned
    matches across all `pos1` is minimized.

    E.g.::

        >>> pos1 = np.array([[20, 10, 30, 40]]).T
        >>> pos2 = np.array([[5, 15, 25, 35, 50]]).T
        >>> matches = match_points(pos1, pos2)
        >>> matches
        array([1, 0, 2, 3])

    Parameters
    ----------
    pos1 : np.ndarray
        2D array of NxK. Where N is number of positions and K is the number
        of dimensions (e.g. 3 for x, y, z).
    pos2 : np.ndarray
        2D array of MxK. Where M is number of positions and K is the number
        of dimensions (e.g. 3 for x, y, z).

        The relationship N <= M must be true.
    threshold : float, optional. Defaults to np.inf.
        The threshold to use to consider a pair a bad match. Any match pair
        whose distance is greater or equal to the threshold will be considered
        to be at great distance to each other.

        It'll still show up in the matching, but it will have the least
        priority for a match because that match will not reduce the overall
        cost across all points.

        Use `analyze_point_matches` subsequently to remove the "bad" matches.

    Returns
    -------
    matches : np.ndarray
        1D array of length N. Each index i in matches corresponds
        to index i in `pos1`. The value of index i in matches is the index
        j in pos2 that is the best match for that pos1.

        I.e. the match is (pos1[i], pos2[matches[i]]).
    """
    # based on https://en.wikipedia.org/wiki/Hungarian_algorithm
    pos1 = pos1.astype(np.float64)
    pos2 = pos2.astype(np.float64)
    # numba pre-checks that arrays are at least 2-dims. Us checking would be
    # too late and never invoked

    if pos1.ndim != 2 or pos2.ndim != 2:
        raise ValueError("The input arrays must have exactly 2 dimensions")

    n_rows = pos1.shape[0]
    n_cols = pos2.shape[0]
    if n_rows > n_cols:
        raise ValueError(
            "The length of pos1 must be less than or equal to length of pos2"
        )
    if pos1.shape[1] != pos2.shape[1]:
        raise ValueError("The two inputs have different number of columns")

    have_threshold = threshold != np.inf

    potentials_rows = np.zeros(n_rows)
    potentials_cols = np.zeros(n_cols + 1)
    assignment_row = np.full(n_cols + 1, -1, dtype=np.int_)
    min_to = np.empty(n_cols + 1, dtype=np.float_)
    # previous worker on alternating path
    prev_col_for_col = np.empty(n_cols + 1, dtype=np.int_)
    # whether col is in use
    col_used = np.zeros(n_cols + 1, dtype=np.bool_)

    # assign row-th match
    for row in range(n_rows):
        col = n_cols
        assignment_row[col] = row
        # min reduced cost over edges from Z to worker w
        min_to[:] = np.inf
        prev_col_for_col[:] = -1
        col_used[:] = False

        # runs at most row + 1 times
        while assignment_row[col] != -1:
            col_used[col] = True
            row_cur = assignment_row[col]
            delta = np.inf
            col_next = -1

            for col_i in range(n_cols):
                if not col_used[col_i]:
                    # use sqrt to match threshold which is in actual distance
                    dist = np.sqrt(
                        np.sum(np.square(pos1[row_cur, :] - pos2[col_i, :]))
                    )
                    if dist == np.inf:
                        raise ValueError(
                            "The distance between point is too large"
                        )
                    if have_threshold and dist > threshold:
                        dist = threshold

                    cur = (
                        dist
                        - potentials_rows[row_cur]
                        - potentials_cols[col_i]
                    )
                    if cur < min_to[col_i]:
                        min_to[col_i] = cur
                        prev_col_for_col[col_i] = col

                    if min_to[col_i] < delta:
                        delta = min_to[col_i]
                        col_next = col_i

            # delta will always be non-negative,
            # except possibly during the first time this loop runs
            # if any entries of C[row] are negative
            for col_i in range(n_cols + 1):
                if col_used[col_i]:
                    potentials_rows[assignment_row[col_i]] += delta
                    potentials_cols[col_i] -= delta
                else:
                    min_to[col_i] -= delta
            col = col_next

        # update assignments along alternating path
        while col != n_cols:
            col_i = prev_col_for_col[col]
            assignment_row[col] = assignment_row[col_i]
            col = col_i

        with objmode():
            __compare_progress()

    # compute match from assignment
    matches = np.empty(n_rows, dtype=np.int_)
    for i in range(n_cols):
        if assignment_row[i] != -1:
            matches[assignment_row[i]] = i

    return matches


@njit
def analyze_point_matches(
    pos1: np.ndarray,
    pos2: np.ndarray,
    matches: np.ndarray,
    threshold: float = np.inf,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Given a matching found by `match_points`, it optionally applies a threshold
    and splits the matched points from unmatched points in a friendlier way.

    E.g.::

        >>> pos1 = np.array([[20, 10, 30, 40, 50]]).T
        >>> pos2 = np.array([[5, 15, 25, 35, 100, 200]]).T
        >>> matches = match_points(pos1, pos2)
        >>> matches
        array([1, 0, 2, 3, 4])
        >>> analyze_point_matches(pos1, pos2, matches)
        (array([], dtype=int64),
         array([[0, 1],
                [1, 0],
                [2, 2],
                [3, 3],
                [4, 4]], dtype=int64),
         array([5], dtype=int64))
         >>> analyze_point_matches(pos1, pos2, matches, threshold=10)
        (array([4], dtype=int64),
         array([[0, 1],
                [1, 0],
                [2, 2],
                [3, 3]], dtype=int64),
         array([4, 5], dtype=int64))

    Parameters
    ----------
    pos1 : np.ndarray
        Same as `match_points`.
    pos2 : np.ndarray
        Same as `match_points`.
    matches : np.ndarray
        The matches returned by `match_points`.
    threshold : float, optional. Defaults to np.inf.
        The threshold to use to remove bad matches. Any match pair whose
        distance is greater than the threshold will be removed from the
        matching and added to the missing_pos1 and missing_pos2 arrays.

        To get a best global optimum, use the same threshold you used in
        `match_points`.

    Returns
    -------
    tuple : (np.ndarray, np.ndarray, np.ndarray)
        missing_pos1: 1d array of all the indices of pos1 that found no match
            in pos2 (sorted).
        good_matches: 2d array with all the (pos1, pos2) indices that remained
            in the matching. It's of size Rx2. It's sorted by the first column.
        missing_pos2: 1d array of all the indices of pos2 that found no match
            in pos1 (sorted).
    """
    # indices and mask on indices
    pos2_n = len(pos2)
    pos2_i = np.arange(pos2_n)
    pos2_unmatched = np.ones(pos2_n, dtype=np.bool_)
    # those in pos2 who have a match in pos1
    pos2_unmatched[matches] = False
    # all the pos2 that have no matches from pos1
    missing_pos2 = pos2_i[pos2_unmatched]

    # repackage matches so the first column is the pos1 idx and 2nd column is
    # the corresponding pos2 index
    matches_indices = np.stack((np.arange(len(pos1)), matches), axis=1)

    dist = np.sqrt(np.sum(np.square(pos1 - pos2[matches, :]), axis=1))
    too_large = dist >= threshold
    bad_matches = matches_indices[too_large, :]
    good_matches = matches_indices[np.logical_not(too_large), :]

    missing_pos1 = bad_matches[:, 0]
    # more missing for pos2 for those above threshold
    missing_pos2 = np.concatenate((missing_pos2, bad_matches[:, 1]))
    missing_pos2 = np.sort(missing_pos2)

    return missing_pos1, good_matches, missing_pos2
