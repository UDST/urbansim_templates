import glob
import os

import pytest


def _remove_config_files():
    for path in glob.glob(os.path.join('configs', '*.yaml')) + \
            glob.glob(os.path.join('configs', '*.pkl')):
        os.remove(path)


@pytest.fixture(autouse=True)
def clean_config_directory():
    """
    Remove configuration files left in ``configs/`` by a test that errored before it
    could remove its own step, whether in an earlier run or earlier in this one.
    ModelManager loads every YAML file it finds there, so a stray file makes unrelated
    tests fail.
    
    """
    _remove_config_files()
    yield
    _remove_config_files()
