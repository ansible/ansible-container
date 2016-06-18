from container.shipit.utils import create_config_output_path
from container.shipit.constants import SHIPIT_CONFIG_PATH


def test_create_config_output_path(tmpdir):
    expected_dir = tmpdir.join(SHIPIT_CONFIG_PATH)
    assert create_config_output_path(str(tmpdir)) == expected_dir


def test_create_config_output_path_exists(tmpdir):
    expected_dir = tmpdir.join(SHIPIT_CONFIG_PATH)
    assert create_config_output_path(str(tmpdir)) == expected_dir
    assert create_config_output_path(str(tmpdir)) == expected_dir
