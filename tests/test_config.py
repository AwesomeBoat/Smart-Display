import pytest
from pathlib import Path
from src.config import *


@pytest.mark.parametrize("file, expected"[
    (LAT, True)
    (LON, True)
])
def test_file_exists(file_path: Path, expected):
    assert isinstance(file_path, Path) == expected
