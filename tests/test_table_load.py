import os

import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import LoadTable
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
    Create some data files on disk.
    
    """
    d1 = {'building_id': np.arange(10),
          'price': 1e6*np.random.random(10)}
    
    bldg = pd.DataFrame(d1).set_index('building_id')
    bldg.to_csv('data/buildings.csv')
    bldg.to_csv('data/buildings.csv.gz', compression='gzip')
    bldg.to_hdf('data/buildings.hdf', key='buildings')
    
    def teardown():
        os.remove('data/buildings.csv')
        os.remove('data/buildings.csv.gz')
        os.remove('data/buildings.hdf')
    
    request.addfinalizer(teardown)


def test_template_validity():
    """
    Run the templates through the standard validation check.
    
    """
    assert validate_template(LoadTable)


def test_property_persistence(orca_session):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    t = LoadTable()
    t.table = 'buildings'
    t.source_type = 'csv'
    t.path = 'data/buildings.csv'
    t.csv_index_cols = 'building_id'
    t.extra_settings = {'make_data_awesome': True}  # unfortunately not a valid setting
    t.cache = False
    t.cache_scope = 'iteration'
    t.copy_col = False
    t.name = 'buildings-csv'
    t.tags = ['awesome', 'data']
    t.autorun = False
    
    d1 = t.to_dict()
    modelmanager.register(t)
    modelmanager.initialize()
    d2 = modelmanager.get_step(t.name).to_dict()
    
    assert d1 == d2
    modelmanager.remove_step(t.name)


def test_csv(orca_session, data):
    """
    Test loading data from a CSV file.
    
    """
    t = LoadTable()
    t.table = 'buildings'
    t.source_type = 'csv'
    t.path = 'data/buildings.csv'
    t.csv_index_cols = 'building_id'
    
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.register(t)
    assert 'buildings' in orca.list_tables()
    _ = orca.get_table('buildings').to_frame()
    
    modelmanager.initialize()
    assert 'buildings' in orca.list_tables()
    
    modelmanager.remove_step(t.name)


def test_hdf(orca_session, data):
    """
    Test loading data from an HDF file.
    
    """
    t = LoadTable()
    t.table = 'buildings'
    t.source_type = 'hdf'
    t.path = 'data/buildings.hdf'
    
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.register(t)
    assert 'buildings' in orca.list_tables()
    _ = orca.get_table('buildings').to_frame()
    
    modelmanager.initialize()
    assert 'buildings' in orca.list_tables()
    
    modelmanager.remove_step(t.name)


def test_extra_settings(orca_session, data):
    """
    Test loading data with extra settings, e.g. for compressed files.
    
    """
    t = LoadTable()
    t.table = 'buildings'
    t.source_type = 'csv'
    t.path = 'data/buildings.csv.gz'
    t.csv_index_cols = 'building_id'
    t.extra_settings = {'compression': 'gzip'}
    
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.register(t)
    assert 'buildings' in orca.list_tables()
    _ = orca.get_table('buildings').to_frame()
    
    modelmanager.initialize()
    assert 'buildings' in orca.list_tables()
    
    modelmanager.remove_step(t.name)


def test_without_autorun(orca_session, data):
    """
    Confirm that disabling autorun works.
    
    """
    t = LoadTable()
    t.table = 'buildings'
    t.source_type = 'csv'
    t.path = 'data/buildings.csv'
    t.csv_index_cols = 'building_id'
    t.autorun = False
    
    modelmanager.register(t)
    assert 'buildings' not in orca.list_tables()
    
    modelmanager.remove_step(t.name)
    
    
    