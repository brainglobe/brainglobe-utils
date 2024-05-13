from pathlib import Path
from typing import Tuple, Union

import numpy as np
from scipy.ndimage import zoom
from skimage.filters import gaussian

from brainglobe_utils.general.system import ensure_directory_exists
from brainglobe_utils.image.binning import get_bins
from brainglobe_utils.image.masking import mask_image_threshold
from brainglobe_utils.image.scale import scale_and_convert_to_16_bits
from brainglobe_utils.IO.image import to_tiff


def rescale_array(source_array, target_array, order=1):
    """
    Rescale a source array to the size of a target array.

    Parameters
    ----------
    source_array : np.ndarray
        The array to be rescaled.
    target_array : np.ndarray
        The array whose size will be matched.
    order : int (default=1)
    Returns
    -------
    np.ndarray
        The rescaled source array.
    """

    # Compute the zoom factors for each dimension
    zoom_factors = [
        t / s for s, t in zip(source_array.shape, target_array.shape)
    ]

    # Use scipy's zoom function to rescale the array
    rescaled_array = zoom(source_array, zoom_factors, order=order)

    return rescaled_array


def heatmap_from_points(
    points: np.ndarray,
    image_resolution: float,
    image_shape: Tuple[int, int, int],
    bin_sizes: Tuple[int, int, int] = (1, 1, 1),
    output_filename: Union[str, Path, None] = None,
    smoothing: Union[float, None] = None,
    mask_image: Union[np.ndarray, None] = None,
) -> np.ndarray:
    """
    Generate a heatmap from a set of points and a reference image that
    defines the shape and resolution of the heatmap.

    Parameters
    ----------
    points : np.ndarray
        Data points to be used for heatmap generation.
        These may be cell positions, e.g. from cellfinder.
    image_resolution : float
        Resolution of the image to be generated.
    image_shape : Tuple[int, int, int]
        The shape of the downsampled heatmap as a tuple of integers
    bin_sizes : Tuple[int, int, int], optional
        The bin sizes for each dimension of the heatmap (default is (1, 1, 1)).
    output_filename : Union[str, pathlib.Path, None]
        The filename or path where the heatmap image will be saved.
        Can be a string or a pathlib.Path object. If None, the heatmap will
        not be saved
    smoothing : float, optional
        Smoothing factor to be applied to the heatmap. Expressed in "real"
        units (e.g. microns). This will be converted to voxel units based on
        the image_resolution.
        If None, no smoothing is applied (default is None).
    mask_image : Union[np.ndarray, None], optional
        An optional mask image (as a NumPy array) to apply to the heatmap.
        This could be e.g. a registered atlas image (so points outside the
        brain are masked). The image will be
        binarised, so this image can be binary or not.
         If None, no mask is applied (default is None).

    Returns
    -------
    np.ndarray
        The generated heatmap as a NumPy array.
    """

    bins = get_bins(image_shape, bin_sizes)
    heatmap_array, _ = np.histogramdd(points, bins=bins)
    heatmap_array = heatmap_array.astype(np.uint16)

    if smoothing is not None:
        smoothing = int(round(smoothing / image_resolution))
        heatmap_array = gaussian(heatmap_array, sigma=smoothing)

    if mask_image is not None:
        if mask_image.shape != heatmap_array.shape:
            mask_image = rescale_array(mask_image, heatmap_array)

        heatmap_array = mask_image_threshold(heatmap_array, mask_image)

    heatmap_array = scale_and_convert_to_16_bits(heatmap_array)

    if output_filename is not None:
        ensure_directory_exists(Path(output_filename).parent)
        to_tiff(heatmap_array, output_filename)

    return heatmap_array
