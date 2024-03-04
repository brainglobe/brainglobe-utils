import psutil
from scipy.ndimage import zoom


class ImageIOLoadException(Exception):
    pass


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
    BrainLoadException
        If not enough memory is available.
    """
    total_size = img_byte_size * n_imgs
    free_mem = psutil.virtual_memory().available
    if total_size >= free_mem:
        raise ImageIOLoadException(
            "Not enough memory on the system to complete loading operation"
            "Needed {}, only {} available.".format(total_size, free_mem)
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
