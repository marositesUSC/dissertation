from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

sys.path.append(str(SRC_DIR))

from config import get_project_root, load_config


def test_get_project_root():
    project_root = get_project_root()

    assert project_root.exists()
    assert (project_root / "config").exists()
    assert (project_root / "src").exists()


def test_load_paths_config():
    config = load_config("paths.yml")

    assert isinstance(config, dict)
    assert len(config) > 0


def test_missing_config_raises_error():
    missing_file = "this_file_does_not_exist.yml"

    try:
        load_config(missing_file)
    except FileNotFoundError:
        assert True
    else:
        assert False, "Expected FileNotFoundError"