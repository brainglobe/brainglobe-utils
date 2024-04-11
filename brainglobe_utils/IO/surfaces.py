from pathlib import Path
from typing import Tuple, Union

from numpy.typing import NDArray


def marching_cubes_to_obj(
    marching_cubes_out: Tuple[NDArray], output_file: Union[str, Path]
):
    """
    Saves the output of skimage.measure.marching_cubes as an .obj file

    Parameters
    ----------
    marching_cubes_out : tuple of np.ndarray
        Output from skimage.measure.marching_cubes.
    output_file : str or pathlib.Path
        Path of .obj file to write output into.
    """
    verts, faces, normals, _ = marching_cubes_out
    with open(output_file, "w") as f:
        for item in verts:
            f.write(f"v {item[0]} {item[1]} {item[2]}\n")
        for item in normals:
            f.write(f"vn {item[0]} {item[1]} {item[2]}\n")
        for item in faces:
            f.write(
                f"f {item[0]}//{item[0]} {item[1]}//{item[1]} "
                f"{item[2]}//{item[2]}\n"
            )
        f.close()
