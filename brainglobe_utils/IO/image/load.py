import glob
import logging
import math
import os
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Tuple

import numpy as np
import tifffile
from dask import array as da
from dask import delayed
from natsort import natsorted
from skimage import transform
from tqdm import tqdm

from brainglobe_utils.general.system import (
    get_num_processes,
    get_sorted_file_paths,
)
from brainglobe_utils.IO.image.utils import ImageIOLoadException

from .utils import check_mem, scale_z

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    import nibabel as nib


def load_any(
    src_path,
    x_scaling_factor=1.0,
    y_scaling_factor=1.0,
    z_scaling_factor=1.0,
    anti_aliasing=True,
    load_parallel=False,
    sort_input_file=False,
    as_numpy=False,
    n_free_cpus=2,
):
    """
    This function will guess the type of data and hence call the appropriate
    function from this module to load the given brain.

    .. warning:: x and y scaling not used at the moment if loading a
        complete image

    Parameters
    ----------
    src_path : str or pathlib.Path
        Can be the path of a nifty file, tiff file, tiff files
        folder, or text file containing a list of paths.

    x_scaling_factor : float, optional
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float, optional
        The scaling of the brain along the y dimension (applied on loading
        before return).

    z_scaling_factor : float, optional
        The scaling of the brain along the z dimension (applied on loading
        before return).

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    load_parallel : bool, optional
        Load planes in parallel using multiprocessing for faster data loading.

    sort_input_file : bool, optional
        If set to true and the input is a filepaths file, it will be naturally
        sorted.

    as_numpy : bool, optional
        Whether to convert the image to a numpy array in memory (rather than a
        memmap). Only relevant for .nii files.

    verbose : bool, optional
        Print more information about the process.

    n_free_cpus : int, optional
        Number of CPU cores to leave free.

    Returns
    -------
    np.ndarray
        The loaded brain.

    Raises
    ------
    ImageIOLoadException
        If there was an issue loading the image with image.

    See Also
    ------
    image.utils.ImageIOLoadException
    """
    src_path = Path(src_path)

    if src_path.is_dir():
        logging.debug("Data type is: directory of files")
        img = load_from_folder(
            src_path,
            x_scaling_factor,
            y_scaling_factor,
            z_scaling_factor,
            anti_aliasing=anti_aliasing,
            file_extension=".tif*",
            load_parallel=load_parallel,
            n_free_cpus=n_free_cpus,
        )
    elif src_path.suffix == ".txt":
        logging.debug("Data type is: list of file paths")
        img = load_img_sequence(
            src_path,
            x_scaling_factor,
            y_scaling_factor,
            z_scaling_factor,
            anti_aliasing=anti_aliasing,
            load_parallel=load_parallel,
            sort=sort_input_file,
            n_free_cpus=n_free_cpus,
        )
    elif src_path.suffix in [".tif", ".tiff"]:
        logging.debug("Data type is: tif stack")
        img = load_img_stack(
            src_path,
            x_scaling_factor,
            y_scaling_factor,
            z_scaling_factor,
            anti_aliasing=anti_aliasing,
        )
    elif src_path.suffix == ".nii" or str(src_path).endswith(".nii.gz"):
        logging.debug("Data type is: NifTI")
        img = load_nii(src_path, as_array=True, as_numpy=as_numpy)
    else:
        raise NotImplementedError(
            "Could not guess data type for path {}".format(src_path)
        )

    return img


def load_img_stack(
    stack_path,
    x_scaling_factor,
    y_scaling_factor,
    z_scaling_factor,
    anti_aliasing=True,
):
    """
    Load a tiff stack as a numpy array.

    Parameters
    ----------
    stack_path : str or pathlib.Path
        The path of the image to be loaded. Note that only 3D tiffs are
        supported.

    x_scaling_factor : float
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float
        The scaling of the brain along the y dimension (applied on loading
        before return).

    z_scaling_factor : float
        The scaling of the brain along the z dimension (applied on loading
        before return).

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    Returns
    -------
    np.ndarray
        The loaded brain array.

    Raises
    ------
    ImageIOLoadException
        If attempt to load a 2D tiff.
    """
    stack_path = Path(stack_path)
    logging.debug(f"Loading: {stack_path}")
    stack = tifffile.imread(stack_path)

    if stack.ndim != 3:
        raise ImageIOLoadException(error_type="2D tiff")

    # Downsampled plane by plane because the 3D downsampling in scipy etc
    # uses too much RAM

    if not (x_scaling_factor == y_scaling_factor == 1):
        downsampled_stack = []
        logging.debug("Downsampling stack in X/Y")
        for plane in tqdm(range(0, len(stack))):
            downsampled_stack.append(
                transform.rescale(
                    stack[plane],
                    (y_scaling_factor, x_scaling_factor),
                    mode="constant",
                    preserve_range=True,
                    anti_aliasing=anti_aliasing,
                )
            )

        logging.debug("Converting downsampled stack to array")
        stack = np.array(downsampled_stack)

    if z_scaling_factor != 1:
        logging.debug("Downsampling stack in Z")
        stack = scale_z(stack, z_scaling_factor)
    return stack


def load_nii(src_path, as_array=False, as_numpy=False):
    """
    Load a brain from a nifti file.

    Parameters
    ----------
    src_path : str or pathlib.Path
        The path to the nifty file on the filesystem.

    as_array : bool, optional
        Whether to convert the brain to a numpy array or keep it as a nifty
        object.

    as_numpy : bool, optional
        Whether to convert the image to a numpy array in memory (rather than a
        memmap).

    Returns
    -------
    np.ndarray or nifty object
        The loaded brain. The format depends on the `as_array` flag.
    """
    src_path = Path(src_path)
    nii_img = nib.load(src_path)
    if as_array:
        image = nii_img.get_fdata()
        if as_numpy:
            image = np.array(image)

        return image
    else:
        return nii_img


def load_from_folder(
    src_folder,
    x_scaling_factor=1,
    y_scaling_factor=1,
    z_scaling_factor=1,
    anti_aliasing=True,
    file_extension="",
    load_parallel=False,
    n_free_cpus=2,
):
    """
    Load a brain from a folder. All tiff files will be read sorted and assumed
    to belong to the same sample. Optionally, a name_filter string can be
    supplied which will have to be present in the file names for them to be
    considered part of the sample.

    Parameters
    ----------
    src_folder : str or pathlib.Path
        The source folder containing tiff files. Note that this folder must
        contain at least 2 tiffs, and all tiff images must have the same shape.

    x_scaling_factor : float, optional
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float, optional
        The scaling of the brain along the y dimension (applied on loading
        before return).

    z_scaling_factor : float, optional
        The scaling of the brain along the z dimension.

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    file_extension : str, optional
        Will have to be present in the file names for them to be considered
        part of the sample.

    load_parallel : bool, optional
        Use multiprocessing to speed up image loading.

    n_free_cpus : int, optional
        Number of CPU cores to leave free.

    Returns
    -------
    np.ndarray
        The loaded and scaled brain.

    Raises
    ------
    ImageIOLoadException
        If attempt to load a directory containing only a single tiff, or a
        sequence of tiffs that have different shapes.
    """
    paths = get_sorted_file_paths(src_folder, file_extension=file_extension)

    return load_image_series(
        paths,
        x_scaling_factor,
        y_scaling_factor,
        z_scaling_factor,
        load_parallel=load_parallel,
        n_free_cpus=n_free_cpus,
        anti_aliasing=anti_aliasing,
    )


def load_img_sequence(
    img_sequence_file_path,
    x_scaling_factor=1,
    y_scaling_factor=1,
    z_scaling_factor=1,
    anti_aliasing=True,
    load_parallel=False,
    sort=False,
    n_free_cpus=2,
):
    """
    Load a brain from a sequence of files specified in a text file containing
    an ordered list of paths.

    Parameters
    ----------
    img_sequence_file_path : str or pathlib.Path
        The path to the file containing the ordered list of image paths (one
        per line). Note that this file must contain at least 2 paths, and all
        referenced images must have the same shape.

    x_scaling_factor : float, optional
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float, optional
        The scaling of the brain along the y dimension (applied on loading
        before return).

    z_scaling_factor : float, optional
        The scaling of the brain along the z dimension.

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    load_parallel : bool, optional
        Use multiprocessing to speed up image loading.

    sort : bool, optional
        If set to true, will perform a natural sort of the file paths in the
        list.

    n_free_cpus : int, optional
        Number of CPU cores to leave free.

    Returns
    -------
    np.ndarray
        The loaded and scaled brain.

    Raises
    ------
    ImageIOLoadException
        If attempt to load a txt file containing only a single path, or a
        sequence of paths that load images with different shapes.
    """
    img_sequence_file_path = Path(img_sequence_file_path)
    with open(img_sequence_file_path, "r") as in_file:
        paths = in_file.readlines()
        paths = [p.strip() for p in paths]
    if sort:
        paths = natsorted(paths)

    return load_image_series(
        paths,
        x_scaling_factor,
        y_scaling_factor,
        z_scaling_factor,
        load_parallel=load_parallel,
        n_free_cpus=n_free_cpus,
        anti_aliasing=anti_aliasing,
    )


def load_image_series(
    paths,
    x_scaling_factor=1,
    y_scaling_factor=1,
    z_scaling_factor=1,
    anti_aliasing=True,
    load_parallel=False,
    n_free_cpus=2,
):
    """
    Load a brain from a sequence of image paths.

    Parameters
    ----------
    paths : list of str or list of pathlib.Path
        Ordered list of image paths. Must contain at least 2 paths, and all
        referenced images must have the same shape.

    x_scaling_factor : float, optional
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float, optional
        The scaling of the brain along the y dimension (applied on loading
        before return).

    z_scaling_factor : float, optional
        The scaling of the brain along the z dimension.

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    load_parallel : bool, optional
        Use multiprocessing to speed up image loading.

    n_free_cpus : int, optional
        Number of CPU cores to leave free.

    Returns
    -------
    np.ndarray
        The loaded and scaled brain.

    Raises
    ------
    ImageIOLoadException
        If attempt to load a single path, or a sequence of paths that load
        images with different shapes.
    """
    # Throw an error if there's only one image to load - should be an image
    # series, so at least 2 paths.
    if len(paths) == 1:
        raise ImageIOLoadException("single_tiff")

    if load_parallel:
        img = threaded_load_from_sequence(
            paths,
            x_scaling_factor,
            y_scaling_factor,
            n_free_cpus=n_free_cpus,
            anti_aliasing=anti_aliasing,
        )
    else:
        img = load_from_paths_sequence(
            paths,
            x_scaling_factor,
            y_scaling_factor,
            anti_aliasing=anti_aliasing,
        )

    img = np.moveaxis(img, 2, 0)  # back to z first
    if z_scaling_factor != 1:
        img = scale_z(img, z_scaling_factor)

    return img


def threaded_load_from_sequence(
    paths_sequence,
    x_scaling_factor=1.0,
    y_scaling_factor=1.0,
    anti_aliasing=True,
    n_free_cpus=2,
):
    """
    Use multiprocessing to load a brain from a sequence of image paths.

    Parameters
    ----------
    paths_sequence : list of str or list of pathlib.Path
        The sorted list of the planes paths on the filesystem. All planes
        must have the same shape.

    x_scaling_factor : float, optional
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float, optional
        The scaling of the brain along the y dimension (applied on loading
        before return).

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    n_free_cpus : int, optional
        Number of CPU cores to leave free.

    Returns
    -------
    np.ndarray
        The loaded and scaled brain.

    Raises
    ------
    ImageIOLoadException
        If attempt to load a sequence of images with different shapes.
    """
    stacks = []
    n_processes = get_num_processes(min_free_cpu_cores=n_free_cpus)

    # WARNING: will not work with interactive interpreter.
    pool = ProcessPoolExecutor(max_workers=n_processes)
    # FIXME: should detect and switch to other method

    n_paths_per_subsequence = math.ceil(len(paths_sequence) / n_processes)
    for i in range(n_processes):
        start_idx = i * n_paths_per_subsequence
        if start_idx >= len(paths_sequence):
            break
        else:
            end_idx = start_idx + n_paths_per_subsequence

            if end_idx <= len(paths_sequence):
                sub_paths = paths_sequence[start_idx:end_idx]
            else:
                sub_paths = paths_sequence[start_idx:]

        process = pool.submit(
            load_from_paths_sequence,
            sub_paths,
            x_scaling_factor,
            y_scaling_factor,
            anti_aliasing=anti_aliasing,
        )
        stacks.append(process)

    stack_shapes = set()
    for i in range(len(stacks)):
        stacks[i] = stacks[i].result()
        stack_shapes.add(stacks[i].shape[0:2])

    # Raise an error if the x/y shape of all stacks aren't the same
    if len(stack_shapes) > 1:
        raise ImageIOLoadException("sequence_shape")

    stack = np.dstack(stacks)
    return stack


def load_from_paths_sequence(
    paths_sequence,
    x_scaling_factor=1.0,
    y_scaling_factor=1.0,
    anti_aliasing=True,
):
    # TODO: Optimise -  load threaded and process by batch
    """
    A single core version of the function to load a brain from a sequence of
    image paths.

    Parameters
    ----------
    paths_sequence : list of str or list of pathlib.Path
        The sorted list of the planes paths on the filesystem. All planes
        must have the same shape.

    x_scaling_factor : float, optional
        The scaling of the brain along the x dimension (applied on loading
        before return).

    y_scaling_factor : float, optional
        The scaling of the brain along the y dimension (applied on loading
        before return).

    anti_aliasing : bool, optional
        Whether to apply a Gaussian filter to smooth the image prior to
        down-scaling. It is crucial to filter when down-sampling the image to
        avoid aliasing artifacts.

    Returns
    -------
    np.ndarray
        The loaded and scaled brain.

    Raises
    ------
    ImageIOLoadException
        If attempt to load a sequence of images with different shapes.
    """
    for i, p in enumerate(
        tqdm(paths_sequence, desc="Loading images", unit="plane")
    ):
        img = tifffile.imread(p)
        if i == 0:
            check_mem(
                img.nbytes * x_scaling_factor * y_scaling_factor,
                len(paths_sequence),
            )
            # TEST: add test case for shape rounding
            volume = np.empty(
                (
                    int(round(img.shape[0] * x_scaling_factor)),
                    int(round(img.shape[1] * y_scaling_factor)),
                    len(paths_sequence),
                ),
                dtype=img.dtype,
            )
        if x_scaling_factor != 1 or y_scaling_factor != 1:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                img = transform.rescale(
                    img,
                    (x_scaling_factor, y_scaling_factor),
                    mode="constant",
                    preserve_range=True,
                    anti_aliasing=anti_aliasing,
                )

        # Raise an error if the shapes of the images aren't the same
        if not volume[:, :, i].shape == img.shape:
            raise ImageIOLoadException("sequence_shape")
        volume[:, :, i] = img
    return volume


def get_size_image_from_file_paths(file_path, file_extension="tif"):
    """
    Returns the size of an image (which is a list of 2D tiff files or a
    single-file tif stack), without loading the whole image.

    Parameters
    ----------
    file_path : str or pathlib.Path
        Filepath of text file containing paths of all 2D files, a
        filepath of a directory containing all 2D files, or a single
        tiff file z-stack.

    file_extension : str, optional
        Optional file extension (if a directory is passed).

    Returns
    -------
    dict
        Dict of image sizes.
    """
    file_path = Path(file_path)
    if file_path.suffix in [".tif", ".tiff"]:
        # read just the metadata
        with tifffile.TiffFile(file_path) as tiff:
            if not len(tiff.series):
                raise ValueError(
                    f"Attempted to load {file_path} but didn't find a z-stack"
                )
            if len(tiff.series) != 1:
                raise ValueError(
                    f"Attempted to load {file_path} but found multiple stacks"
                )

            shape = tiff.series[0].shape
            axes = tiff.series[0].axes.lower()

            if len(shape) != 3:
                raise ValueError(
                    f"Attempted to load {file_path} but didn't find a "
                    f"3-dimensional stack. Found {axes} axes "
                    f"with shape {shape}"
                )
            # axes is e.g. "zxy"
            if set(axes) == {"x", "y", "z"}:
                image_shape = {ax: n for ax, n in zip(axes, shape)}
                return image_shape
            else:  # metadata does not specify axes as expected,
                logging.debug(
                    f"Axis metadata is {axes}, "
                    "which is not the expected set of x,y,z in any order. "
                    "Assume z,y,x"
                )
                image_shape = {
                    ax: n
                    for ax, n in zip(["z", "y", "x"], tiff.series[0].shape)
                }
                return image_shape

    img_paths = get_sorted_file_paths(file_path, file_extension=file_extension)
    z_shape = len(img_paths)

    logging.debug(
        "Loading file: {} to check raw image size" "".format(img_paths[0])
    )
    image_0 = tifffile.imread(img_paths[0])
    y_shape, x_shape = image_0.shape

    image_shape = {"x": x_shape, "y": y_shape, "z": z_shape}
    return image_shape


def get_tiff_meta(
    path: str,
) -> Tuple[Tuple[int, int], np.dtype]:
    with tifffile.TiffFile(path) as tfile:
        nz = len(tfile.pages)
        if not nz:
            raise ValueError(f"tiff file {path} has no pages!")
        first_page = tfile.pages[0]

    return tfile.pages[0].shape, first_page.dtype


lazy_imread = delayed(tifffile.imread)  # lazy reader


def read_z_stack(path):
    """
    Reads z-stack, lazily, if possible.

    If it's a text file or folder with 2D tiff files use dask to read lazily,
    otherwise it's a single file tiff stack and is read into memory.

    :param path: Filename of text file listing 2D tiffs, folder of 2D tiffs,
        or single file tiff z-stack.
    :return: The data as a dask/numpy array.
    """
    if path.endswith(".tiff") or path.endswith(".tif"):
        with tifffile.TiffFile(path) as tiff:
            if not len(tiff.series):
                raise ValueError(
                    f"Attempted to load {path} but couldn't read a z-stack"
                )
            if len(tiff.series) != 1:
                raise ValueError(
                    f"Attempted to load {path} but found multiple stacks"
                )

            axes = tiff.series[0].axes.lower()
            if set(axes) != {"x", "y", "z"}:
                # log that metadata does not specify expected axes
                logging.debug(
                    f"Axis metadata is {axes}, "
                    "which is not the expected set of x,y,z in any order. "
                    "Assume z,y,x"
                )

        return tifffile.imread(path)

    return read_with_dask(path)


def read_with_dask(path):
    """
    Based on https://github.com/tlambert03/napari-ndtiffs
    Reads a folder of tiffs lazily.

    Note that it will make tifffile.imread ignore OME metadata,
    because this can cause issues with correct metadata reading.
    See https://forum.image.sc/t/tifffile-opening-individual-ome-tiff-files-as-single-huge-array-even-when-isolated/77701

    :param path: folder with tifs.
    :return: dask array containing stack of tifs
    """
    path = str(path)
    if path.endswith(".txt"):
        with open(path, "r") as f:
            filenames = [line.rstrip() for line in f.readlines()]

    else:
        filenames = glob.glob(os.path.join(path, "*.tif")) or glob.glob(
            os.path.join(path, "*.tiff")
        )
        if not filenames:
            raise ValueError(
                f"Folder {path} does not contain any .tif or .tiff files"
            )

    shape, dtype = get_tiff_meta(filenames[0])
    lazy_arrays = [
        lazy_imread(fn, is_ome=False)
        for fn in get_sorted_file_paths(filenames)
    ]
    dask_arrays = [
        da.from_delayed(delayed_reader, shape=shape, dtype=dtype)
        for delayed_reader in lazy_arrays
    ]
    stack = da.stack(dask_arrays, axis=0)
    return stack
