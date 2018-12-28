import os

import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.io import Table
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca session and initialize ModelManager.
    
    """
    orca.clear_all()
    modelmanager.initialize()


@pytest.fixture
def data(request):
    """
    Create data files on disk.
    
    """
    d1 = {'building_id': np.arange(10),
          'price': 1e6*np.random.random(10)}
    
    bldg = pd.DataFrame(d1).set_index('building_id')
    bldg.to_csv('data/buildings.csv')
    
    def teardown():
        os.remove('data/buildings.csv')
    
    request.addfinalizer(teardown)


def test_template_validity():
    """
    Run the template through the standard validation check.
    
    """
    assert validate_template(Table)


def test_property_persistence(orca_session):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    pass


# test parameters make it through a save

# test multiple index columns
# test that validation works

# test loading an h5 file works
# test passing cache settings

# call it TableStep?
# tear down data


def test_csv(orca_session, data):
    """
    Test that loading data from a CSV works.
    
    """
    s = Table()
    s.name = 'buildings'
    s.source_type = 'csv'
    s.path = 'data/buildings.csv'
    s.csv_index_cols = 'building_id'
    
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.register(s)
    assert 'buildings' in orca.list_tables()
    
    modelmanager.initialize()
    assert 'buildings' in orca.list_tables()
    
    modelmanager.remove_step('buildings')


def test_without_autorun(orca_session, data):
    """
    Confirm that disabling autorun works.
    
    """
    s = Table()
    s.name = 'buildings'
    s.source_type = 'csv'
    s.path = 'data/buildings.csv'
    s.csv_index_cols = 'building_id'
    s.autorun = False
    
    modelmanager.register(s)
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.remove_step('buildings')
    
    
    
    