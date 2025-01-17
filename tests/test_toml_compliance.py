import json
from pathlib import Path
import unittest

import tomli
from . import burntsushi


class MissingFile:
    def __init__(self, path: Path):
        self.path = path


DATA_DIR = Path(__file__).parent / "data" / "toml-lang-compliance"

VALID_FILES = tuple((DATA_DIR / "valid").glob("**/*.toml"))
# VALID_FILES_EXPECTED = tuple(
#     json.loads(p.with_suffix(".json").read_bytes().decode()) for p in VALID_FILES
# )
_expected_files = []
for p in VALID_FILES:
    json_path = p.with_suffix(".json")
    try:
        text = json.loads(json_path.read_bytes().decode())
    except FileNotFoundError:
        text = MissingFile(json_path)
    _expected_files.append(text)

VALID_FILES_EXPECTED = tuple(_expected_files)
INVALID_FILES = tuple((DATA_DIR / "invalid").glob("**/*.toml"))


class TestTOMLCompliance(unittest.TestCase):
    def test_invalid(self):
        for invalid in INVALID_FILES:
            with self.subTest(msg=invalid.stem):
                toml_str = invalid.read_bytes().decode()
                with self.assertRaises(tomli.TOMLDecodeError):
                    tomli.loads(toml_str)

    def test_valid(self):
        for valid, expected in zip(VALID_FILES, VALID_FILES_EXPECTED):
            with self.subTest(msg=valid.stem):
                if isinstance(expected, MissingFile):
                    # Would be nice to xfail here, but unittest doesn't seem
                    # to allow that in a nice way.
                    continue
                toml_str = valid.read_bytes().decode()
                actual = tomli.loads(toml_str)
                actual = burntsushi.convert(actual)
                expected = burntsushi.normalize(expected)
                self.assertEqual(actual, expected)
