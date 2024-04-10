"""
Cell position I/O

Based on https://github.com/SainsburyWellcomeCentre/niftynet_cell_count by
Christian Niedworok (https://github.com/cniedwor).
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Union
from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as EtElement

import pandas as pd
import yaml

from brainglobe_utils.cells.cells import (
    Cell,
    MissingCellsError,
    UntypedCell,
    pos_from_file_name,
)
from brainglobe_utils.general.system import replace_extension


def get_cells(
    cells_file_path: str,
    cells_only: bool = False,
    cell_type: Optional[int] = None,
):
    """
    Read cells from a file or directory.

    Parameters
    ----------
    cells_file_path : str
        Path to cells file to read. Can be .xml, .yml, or a directory.
    cells_only : bool, optional
        Only relevant for .xml files. If True, will only read Cells with
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
    if cells_file_path.endswith(".xml"):
        return get_cells_xml(cells_file_path, cells_only=cells_only)
    elif cells_file_path.endswith(".yml"):
        return get_cells_yml(cells_file_path, ignore_type=True)
    elif os.path.isdir(cells_file_path):
        try:
            return get_cells_dir(cells_file_path, cell_type=cell_type)
        except IndexError:
            # if a directory is given, but it contains
            # files that can't be read. Usually if the user gives the wrong
            # directory as input to `cellfinder_gen_cubes`
            raise_cell_read_error(cells_file_path)
    else:
        raise_cell_read_error(cells_file_path)


def raise_cell_read_error(cells_file_path):
    """Raise a NotImplementedError, with an informative message including the
    cells file path"""
    logging.error(
        "File format of: {} is not supported or contains errors. Please "
        "supply an xml file, or a directory of files with positions in the "
        "filenames."
        "".format(cells_file_path)
    )
    raise NotImplementedError(
        "File format of: {} is not supported or contains errors. Please "
        "supply an xml file, or a directory of files with positions in the "
        "filenames."
        "".format(cells_file_path)
    )


def get_cells_xml(
    xml_file_path: Union[str, Path], cells_only: Optional[bool] = False
):
    """
    Read cells from an xml file.

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


def get_cells_yml(
    cells_file_path: Union[str, Path],
    ignore_type: Optional[bool] = False,
    marker: Optional[str] = "markers",
):
    """
    Read cells from a yml file.

    Parameters
    ----------
    cells_file_path : str or pathlib.Path
        Path to yml file to read from.
    ignore_type : bool, optional
        Whether to ignore the type of cells - all will be assigned type
        Cell.UNKNOWN. Currently only True is supported.
    marker : str, optional
        Yaml key under which cells information is stored.

    Returns
    -------
    list of Cell
        A list of the cells contained in the file.
    """
    if not ignore_type:
        raise NotImplementedError(
            "Parsing cell types is not yet implemented for YAML files. "
            "Currently the only option is to merge them. Please try again with"
            " 'ignore_type=True'."
        )
    else:
        with open(cells_file_path, "r") as yml_file:
            data = yaml.safe_load(yml_file)
        cells = []
        for cell_type in list(data.keys()):
            type_dict = data[cell_type]
            if marker in type_dict.keys():
                for cell in type_dict[marker]:
                    cells.append(Cell(cell, Cell.UNKNOWN))
    return cells


def get_cells_dir(
    cells_file_path: Union[str, Path], cell_type: Optional[bool] = None
):
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
    cells,
    xml_file_path,
    save_csv=False,
    indentation_str="  ",
    artifact_keep=True,
):
    """
    Save cells to a file.

    Parameters
    ----------
    cells : list of Cell
        Cells to save to file.
    xml_file_path : str
        File path of xml file to save cells to.
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
    # Assume always save xml file, and maybe save other formats
    cells_to_xml(
        cells,
        xml_file_path,
        indentation_str=indentation_str,
        artifact_keep=artifact_keep,
    )

    if save_csv:
        csv_file_path = replace_extension(xml_file_path, "csv")
        cells_to_csv(cells, csv_file_path)


def cells_to_xml(
    cells: List[Cell],
    xml_file_path: Union[str, Path],
    indentation_str: Optional[str] = "  ",
    artifact_keep: Optional[bool] = True,
):
    """
    Save cells to an xml file.

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


def cells_xml_to_df(xml_file_path):
    """Read cells from xml file and convert to dataframe"""
    cells = get_cells(xml_file_path)
    return cells_to_dataframe(cells)


def cells_to_dataframe(cells: List[Cell]) -> pd.DataFrame:
    return pd.DataFrame([c.to_dict() for c in cells])


def cells_to_csv(cells: List[Cell], csv_file_path: Union[str, Path]):
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
