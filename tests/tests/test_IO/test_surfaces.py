from pathlib import Path

from skimage import measure
from skimage.draw import ellipsoid
from brainglobe_utils.IO.surfaces import marching_cubes_to_obj


test_obj = Path(__file__).parent.parent.parent / "data" / "IO"/ "obj" / "test.obj"
def compare_text_files(a, b):
    with open(a, 'r') as file1:
        a_contents = file1.readlines()
    with open(b, 'r') as file2:
        b_contents = file2.readlines()
    assert a_contents == b_contents


def test_marching_cubes_to_obj(tmp_path):

    output_file = tmp_path / "test.obj"
    ellip_base = ellipsoid(6, 10, 16, levelset=True)
    marching_cubes_out = measure.marching_cubes(ellip_base, 0)
    marching_cubes_to_obj(marching_cubes_out, output_file)
    compare_text_files(output_file, test_obj)