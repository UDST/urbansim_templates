import glob
import os

import pytest


@pytest.fixture(scope='session', autouse=True)
def clean_config_directory():
    """
    Remove configuration files left in ``configs/`` by an earlier run that errored
    partway through a test. ModelManager loads every YAML file it finds there, so a
    stray file makes unrelated tests fail.
    
    """
    for path in glob.glob(os.path.join('configs', '*.yaml')) + \
            glob.glob(os.path.join('configs', '*.pkl')):
        os.remove(path)
