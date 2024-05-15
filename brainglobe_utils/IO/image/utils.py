import psutil
from scipy.ndimage import zoom


class ImageIOLoadException(Exception):
    """
    Custom exception class for errors found loading images with
    brainglobe_utils.IO.image.load

    Alerts the user of: loading a directory containing only a single .tiff,
    loading a single 2D .tiff, loading an image sequence where all 2D images
    don't have the same shape, lack of memory to complete loading.

    Set the error message to self.message to read during testing.
    """

    def __init__(self, error_type=None, total_size=None, free_mem=None):
        if error_type == "single_tiff":
            self.message = (
                "Attempted to load directory containing "
                "a single .tiff file. If the .tiff file "
                "is 3D please pass the full path with "
                "filename. Single 2D .tiff file input is "
                "not supported."
            )

        elif error_type == "2D tiff":
            self.message = "Single 2D .tiff file input is not supported."

        elif error_type == "sequence_shape":
            self.message = (
                "Attempted to load an image sequence where individual 2D "
                "images did not have the same shape. Please ensure all image "
                "files contain the same number of pixels."
            )

        elif error_type == "memory":
            self.message = (
                "Not enough memory on the system to complete "
                "loading operation."
            )
            if total_size is not None and free_mem is not None:
                self.message += (
                    f" Needed {total_size}, only {free_mem} " f"available."
                )

        else:
            self.message = "File failed to load with brainglobe_utils.image."

        super().__init__(self.message)


def check_mem(img_byte_size, n_imgs):
    """
    Checks how much memory is available on the system and compares it to the
    size the stack specified by img_byte_size and n_imgs would take
    once loaded

    Raises an error in case memory is insufficient to load that stack

    Parameters
    ----------
    img_byte_size : int
        The size in bytes of an individual image plane.

    n_imgs : int
        The number of image planes to load.

    Raises
    ------
    ImageIOLoadException
        If not enough memory is available.
    """
    total_size = img_byte_size * n_imgs
    free_mem = psutil.virtual_memory().available
    if total_size >= free_mem:
        raise ImageIOLoadException(
            error_type="memory", total_size=total_size, free_mem=free_mem
        )


def scale_z(volume, scaling_factor):
    """
    Scale the given brain along the z dimension.

    Parameters
    ----------
    volume : np.ndarray
        A brain, typically as a numpy array.

    scaling_factor : float
        The z scaling factor.
    """

    return zoom(volume, (scaling_factor, 1, 1), order=1)
