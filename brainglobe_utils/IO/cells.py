"""
Cell position I/O

Based on https://github.com/SainsburyWellcomeCentre/niftynet_cell_count by
Christian Niedworok (https://github.com/cniedwor).
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import List, NoReturn, Optional, Union
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as EtElement

import pandas as pd
import ryml

import brainglobe_utils
from brainglobe_utils.cells.cells import (
    Cell,
    MissingCellsError,
    UntypedCell,
    pos_from_file_name,
)


def get_cells(
    cells_file_path: str | Path,
    cells_only: bool = False,
    cell_type: Optional[int] = None,
) -> list[Cell]:
    """
    Read cells from a file or directory.

    Parameters
    ----------
    cells_file_path : str
        Path to cells file to read. Can be .xml, .yml, .yaml, or a directory,
        which will be parsed accordingly.
    cells_only : bool, optional
        Only relevant for XML/YAML files. If True, will only read Cells with
        type Cell.CELL i.e. exclude all Cell.ARTIFACT, Cell.UNKNOWN, and
        Cell.NO_CELL.
    cell_type : int, optional
        Only relevant for directories. This determines the type to assign
        to all read cells. Refer to the Cell documentation for
        a full explanation of cell_type options.

    Returns
    -------
    list of Cell
        A list of the cells contained in the file or directory.

    See Also
    --------
    Cell : For full description of cell_type parameter.
    """
    path = Path(cells_file_path).resolve()
    if path.suffix == ".xml":
        return get_cells_xml(cells_file_path, cells_only=cells_only)
    elif path.suffix in (".yaml", ".yml"):
        return get_cells_yaml(cells_file_path, cells_only=cells_only)
    elif path.is_dir():
        try:
            return get_cells_dir(cells_file_path, cell_type=cell_type)
        except IndexError as e:
            # if a directory is given, but it contains
            # files that can't be read. Usually if the user gives the wrong
            # directory as input to `cellfinder_gen_cubes`
            raise_cell_read_error(cells_file_path, e)
    else:
        raise_cell_read_error(cells_file_path)


def raise_cell_read_error(
    cells_file_path: str | Path, e: Exception | None = None
) -> NoReturn:
    """Raise a NotImplementedError, with an informative message including the
    cells file path"""
    logging.error(
        "File format of: {} is not supported or contains errors. Please "
        "supply an XML or YAML file, or a directory of files with positions "
        "in the filenames."
        "".format(cells_file_path)
    )
    exc = NotImplementedError(
        "File format of: {} is not supported or contains errors. Please "
        "supply an XML or YAML file, or a directory of files with positions "
        "in the filenames."
        "".format(cells_file_path)
    )

    if e is None:
        raise exc
    raise exc from e


def get_cells_xml(
    xml_file_path: Union[str, Path], cells_only: Optional[bool] = False
) -> list[Cell]:
    """
    Read cells from an XML file.

    Parameters
    ----------
    xml_file_path : str or pathlib.Path
        Path to xml file to read from.
    cells_only : bool, optional
        Whether to only read Cells with type Cell.CELL i.e. exclude all
        Cell.ARTIFACT, Cell.UNKNOWN, and Cell.NO_CELL.

    Returns
    -------
    list of Cell
        A list of the cells contained in the file.
    """
    with open(xml_file_path, "r") as xml_file:
        root = ElementTree.parse(xml_file).getroot()
        cells = []
        for type_marker in root.find("Marker_Data").findall("Marker_Type"):
            cell_type = int(type_marker.find("Type").text)
            for cell_element in type_marker.findall("Marker"):
                cells.append(Cell(cell_element, cell_type))
        if not cells:
            raise MissingCellsError(
                "No cells found in file {}".format(xml_file_path)
            )
    if cells_only:
        cells = [c for c in cells if c.is_cell()]
    return cells


def get_cells_yaml(
    yaml_file_path: Union[str, Path],
    cells_only: Optional[bool] = False,
) -> list[Cell]:
    """
    Read cells from a YAML file.

    Note: due to how we convert from yaml, json limitations are applied to the
    data. Specifically, any dictionary keys will become strings.

    Parameters
    ----------
    yaml_file_path : str or pathlib.Path
        Path to xml file to read from.
    cells_only : bool, optional
        Whether to only read Cells with type Cell.CELL i.e. exclude all
        Cell.ARTIFACT, Cell.UNKNOWN, and Cell.NO_CELL.

    Returns
    -------
    list of Cell
        A list of the cells contained in the file.
    """
    # approach is based on https://github.com/4C-multiphysics/fourcipp/blob
    # /8d9b5b76320643b54e797224d2dffc3984a3e961/src/fourcipp/utils/yaml_io.py
    # rapdiyaml doesn't directly output python objects. But it can output json.
    # So generate json from the file and use python json to return python
    # objects. This is still orders of mag faster than other yaml libraries
    with open(yaml_file_path, "rb") as yaml_file:
        tree = ryml.parse_in_arena(yaml_file.read())

        # ryml can return the buffer, but due to a bug in Swig, it can't handle
        # giant buffers. So instead pass buffer to be filled in. rapidyaml#526
        # Calculate size of the emitted json and create buffer
        n = ryml.compute_emit_json_length(tree)
        buffer = bytearray(n)
        # generate json into buffer
        res = ryml.emit_json_in_place(tree, buffer)
        assert res.nbytes == n
        # get objects from json
        data = json.loads(buffer)

    if not data or not data.get("CellCounter_Marker_File"):
        raise_cell_read_error(yaml_file_path)

    cell_data = data["candidate_cells"]
    cells = []
    for item in cell_data:
        cell = Cell(
            (item["x"], item["y"], item["z"]),
            cell_type=item["type"],
            metadata=item["metadata"],
        )
        cells.append(cell)

    if not cells:
        raise MissingCellsError(
            "No cells found in file {}".format(yaml_file_path)
        )

    if cells_only:
        cells = [c for c in cells if c.is_cell()]
    return cells


def get_cells_dir(
    cells_file_path: Union[str, Path], cell_type: Optional[bool] = None
) -> list[Cell]:
    """
    Read cells from a directory. Cells will be created based on the filenames
    of files in the directory, one cell per file.

    Parameters
    ----------
    cells_file_path : str or pathlib.Path
        Path to directory containing Cells. Each file in the directory will
        create one Cell, based on its filename. This filename must contain the
        cell's x, y and z position E.g. 'Cell_z358_y564_x4056'
    cell_type : int or str or None, optional
        What type to assign all cells. Refer to the Cell documentation for
        a full explanation of cell_type options.

    Returns
    -------
    list of Cell
        A list of the cells contained in the directory.

    See Also
    --------
    Cell : For full description of cell_type parameter.
    """
    cells = []
    for file in os.listdir(cells_file_path):
        # ignore hidden files
        if not file.startswith("."):
            cells.append(Cell(file, cell_type))
    return cells


def save_cells(
    cells: list[Cell],
    xml_file_path: Path | str,
    save_csv: bool = False,
    indentation_str: str = "  ",
    artifact_keep: bool = True,
) -> None:
    """
    Save cells to a file.

    Parameters
    ----------
    cells : list of Cell
        Cells to save to file.
    xml_file_path : str or Path
        File path of XML or YAML file to save cells to (based on the
        extension - XML for .xml, YAML for .yml or .yaml).
    save_csv : bool, optional
        If True, will save cells to a csv file (rather than xml). This will use
        the given xml_file_path with the .xml extension replaced with .csv.
    indentation_str : str, optional
        String to use for indent in xml file.
    artifact_keep : bool, optional
        Whether to keep cells with type Cell.ARTIFACT in the xml file. If True,
        they are kept but their type is changed to Cell.UNKNOWN. If False, they
        are removed.
    """
    # Assume always save xml/yaml file, and maybe save other formats
    path = Path(xml_file_path)
    if path.suffix == ".xml":
        cells_to_xml(
            cells,
            path,
            indentation_str=indentation_str,
            artifact_keep=artifact_keep,
        )
    elif path.suffix in (".yaml", ".yml"):
        cells_to_yml(
            cells,
            path,
            artifact_keep=artifact_keep,
        )

    if save_csv:
        csv_file_path = path.with_suffix(".csv")
        cells_to_csv(cells, csv_file_path)


def cells_to_xml(
    cells: List[Cell],
    xml_file_path: Union[str, Path],
    indentation_str: Optional[str] = "  ",
    artifact_keep: Optional[bool] = True,
) -> None:
    """
    Save cells to an XML file.

    Parameters
    ----------
    cells : list of Cell
        Cells to save to file.
    xml_file_path : str or pathlib.Path
        Xml file path to write cells to.
    indentation_str : str, optional
        String to use for indent in xml file.
    artifact_keep : bool, optional
        Whether to keep cells with type Cell.ARTIFACT. If True, they
        are kept but their type is changed to Cell.UNKNOWN. If False, they are
        removed.
    """
    xml_data = make_xml(cells, indentation_str, artifact_keep=artifact_keep)
    with open(xml_file_path, "w") as xml_file:
        xml_file.write(str(xml_data, "UTF-8"))


def cells_to_yml(
    cells: List[Cell],
    yml_file_path: Union[str, Path],
    artifact_keep: Optional[bool] = True,
) -> None:
    """
    Save cells to a YAML file.

    Note: due to how we convert to yaml, json limitations are applied to the
    data. Specifically, any dictionary keys will become strings.

    Parameters
    ----------
    cells : list of Cell
        Cells to save to file.
    yml_file_path : str or pathlib.Path
        Yaml file path to write cells to.
    artifact_keep : bool, optional
        Whether to keep cells with type Cell.ARTIFACT. If True, they
        are kept but their type is changed to Cell.UNKNOWN. If False, they are
        removed.
    """
    dicts = [c.to_dict() for c in cells]
    artifact = Cell.ARTIFACT
    unknown = Cell.UNKNOWN

    if artifact_keep:
        # replace artifact as unknown
        for d in dicts:
            if d.get("type") == artifact:
                d["type"] = unknown
    else:
        dicts = [d for d in dicts if d["type"] != artifact]

    data = {
        "brainglobe_utils_version": brainglobe_utils.__version__,
        "CellCounter_Marker_File": True,
        "num_candidates": len(dicts),
        "candidate_cells": dicts,
    }
    yml_data = _dict_to_yaml_string(data)
    with open(yml_file_path, "wb") as yml_file:
        yml_file.write(yml_data)


def cells_xml_to_df(xml_file_path):
    """Read cells from xml file and convert to dataframe"""
    cells = get_cells(xml_file_path)
    return cells_to_dataframe(cells)


def cells_to_dataframe(cells: list[Cell]) -> pd.DataFrame:
    """
    Takes a list of Cells and return it as a dataframe.

    The dataframe includes all the items from the Cell's metadata dict as well
    as everything returned by Cell.to_dict(), excluding the metadata keyword.
    I.e. the items in metadata gets promoted to be columns in the dataframe.
    """
    dicts = []
    for c in cells:
        d = c.metadata.copy()
        d.update({k: v for k, v in c.to_dict().items() if k != "metadata"})
        dicts.append(d)

    return pd.DataFrame(dicts)


def cells_to_csv(cells: list[Cell], csv_file_path: Union[str, Path]) -> None:
    """Save cells to csv file"""
    df = cells_to_dataframe(cells)
    df.to_csv(csv_file_path)


def make_xml(cell_list, indentation_str, artifact_keep=True):
    """
    Convert a list of cells to xml.

    Parameters
    ----------
    cell_list : list of Cell
        Cells to convert to xml.
    indentation_str : str
        String to use for indent in xml file.
    artifact_keep : bool, optional
        Whether to keep cells with type Cell.ARTIFACT. If True, they
        are kept but their type is changed to Cell.UNKNOWN. If False, they are
        removed.

    Returns
    -------
    bytes
        Cell list as xml, ready to be saved into a file.
    """
    root = EtElement("CellCounter_Marker_File")
    image_properties = EtElement("Image_Properties")
    file_name = EtElement("Image_Filename")
    file_name.text = "placeholder.tif"
    image_properties.append(file_name)
    root.append(image_properties)

    marker_data = EtElement("Marker_Data")
    current_type = EtElement("Current_Type")
    current_type.text = str(1)  # TODO: check
    marker_data.append(current_type)

    cell_dict = make_type_dict(cell_list)

    # if artifacts exist, do something with them (convert/delete)
    if Cell.ARTIFACT in cell_dict:
        cell_dict = deal_with_artifacts(cell_dict, artifact_keep=artifact_keep)

    for cell_type, cells in cell_dict.items():
        type_el = EtElement("Type")
        type_el.text = str(cell_type)
        mt = EtElement("Marker_Type")
        mt.append(type_el)
        for cell in cells:
            mt.append(cell.to_xml_element())
        marker_data.append(mt)
    root.append(marker_data)

    return pretty_xml(root, indentation_str)


def deal_with_artifacts(cell_dict, artifact_keep=True):
    """Deal with cells with type Cell.ARTIFACT in a cell dict. If artifact_keep
    is True, then convert all Cell.ARTIFACT to Cell.UNKNOWN. Otherwise, remove
    all Cell.ARTIFACT"""
    # What do we want to do with the artifacts (if they exist)?
    # Might want to keep them for training
    if artifact_keep:
        logging.debug("Keeping artifacts")
        # Change their type
        for idx, artifact in enumerate(cell_dict[Cell.ARTIFACT]):
            cell_dict[Cell.ARTIFACT][idx].type = Cell.UNKNOWN
        # Add them to "cell_type = UNKNOWN" list
        cell_dict[Cell.UNKNOWN].extend(cell_dict[Cell.ARTIFACT])
    else:
        logging.debug("Removing artifacts")
    del cell_dict[Cell.ARTIFACT]  # outside if, needs to be run regardless
    return cell_dict


def make_type_dict(cell_list):
    """Convert a list of Cells to a dictionary with keys of cell type and
    values of the list of corresponding cells."""
    types = sorted(set([cell.type for cell in cell_list]))
    return {
        cell_type: [cell for cell in cell_list if cell.type == cell_type]
        for cell_type in types
    }


def pretty_xml(elem, indentation_str="  "):
    """Convert xml element to pretty version, using given indentation string"""
    ugly_xml = ElementTree.tostring(elem, "utf-8")
    md_parsed = minidom.parseString(ugly_xml)
    return md_parsed.toprettyxml(indent=indentation_str, encoding="UTF-8")


def find_relevant_tiffs(tiffs, cell_def):
    """
    Find tiffs that match those read from cell_def.

    Parameters
    ----------
    tiffs : list of str
        List of paths to tiff files. Each tiff filename must contain the cell's
        x, y and z position.
    cell_def : str
        Path to cells to read. Can be an .xml file, .yml file, or a directory.
        If a directory is passed, each file in the directory will
        create one Cell, based on its filename. Each filename must contain the
        cell's x, y and z position.

    Returns
    -------
    list of str
        Filtered list of paths to tiff files, only including those that match
        cells read from cell_def.
    """
    cells = [UntypedCell(tiff) for tiff in tiffs]
    if os.path.isdir(cell_def):
        relevant_cells = set(
            [UntypedCell(pos_from_file_name(f)) for f in os.listdir(cell_def)]
        )
    else:
        relevant_cells = set(
            [UntypedCell.from_cell(cell) for cell in get_cells(cell_def)]
        )
    return [
        tiffs[pos]
        for (pos, cell) in enumerate(cells)
        if cell in relevant_cells
    ]


def _dict_to_yaml_string(data: dict) -> bytearray | bytes:
    """
    Dump dict to yaml and return it as a buffer.

    :param data: dict
        Data to dump.
    :return: A bytes/bytearray with the encoded data.
    """
    # based on https://github.com/4C-multiphysics/fourcipp/blob/
    # 8d9b5b76320643b54e797224d2dffc3984a3e961/src/fourcipp/utils/yaml_io.py
    # see get_cells_yaml for the approach
    # convert data to json encoded text. And then convert into a ryml tree
    tree = ryml.parse_in_arena(json.dumps(data).encode("utf8"))

    # remove all style bits to enable a YAML style output
    # see https://github.com/biojppm/rapidyaml/issues/520
    for node_id, _ in ryml.walk(tree):
        if tree.is_map(node_id) or tree.is_seq(node_id):
            tree.set_container_style(node_id, ryml.NOTYPE)

        if tree.has_key(node_id):
            tree.set_key_style(node_id, ryml.NOTYPE)

        if tree.has_val(node_id):
            tree.set_val_style(node_id, ryml.NOTYPE)

    # ryml can return the buffer, but due to a bug in Swig, it can't handle
    # giant buffers. So instead pass buffer to be filled in. rapidyaml#526
    # Calculate size of the emitted yaml and create buffer
    n = ryml.compute_emit_yaml_length(tree)
    buffer = bytearray(n)
    # generate yaml into buffer
    res = ryml.emit_yaml_in_place(tree, buffer)
    assert res.nbytes == n

    return buffer


def is_brainglobe_xml(path: str | Path) -> bool:
    """
    Takes a potential brainglobe generated XML file and inspects it and returns
    whether this is indeed a brainglobe XML file.

    Note: it does not validate the file for valid XML, only that it contains
    a marker emitted by brainglobe for XML files.
    """
    path = Path(path).resolve()

    try:
        with open(path, "r") as xml_file:
            while line := xml_file.readline():
                if line.strip() == "<CellCounter_Marker_File>":
                    return True
    except Exception:
        pass

    return False


def is_brainglobe_yaml(path):
    """
    Takes a potential brainglobe generated YAML file and inspects it and
    returns whether this is indeed a brainglobe YAML file.

    Note: it does not validate the file for valid YAML, only that it contains
    a marker emitted by brainglobe for YAML files.
    """
    pat = re.compile("^CellCounter_Marker_File *: *true")
    match = re.match
    path = Path(path).resolve()

    try:
        with open(path, "r") as yml_file:
            while line := yml_file.readline():
                if match(pat, line) is not None:
                    return True
    except Exception:
        pass

    return False
