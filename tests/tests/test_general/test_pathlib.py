from pathlib import Path

from brainglobe_utils.general.pathlib import append_to_pathlib_stem


def test_append_to_pathlib_stem():
    path = Path("path", "to", "file.txt")
    appended_path = append_to_pathlib_stem(path, "_appended")
    assert appended_path == Path("path", "to", "file_appended.txt")
