import os

import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import SaveData
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca session and initialize ModelManager.
    
    """
    orca.clear_all()
    modelmanager.initialize()


@pytest.fixture
def data():
    """
    Create a data table.
    
    """
    d1 = {'building_id': np.arange(10),
          'price': (1e6*np.random.random(10)).astype(int)}
    
    df = pd.DataFrame(d1).set_index('building_id')
    
    orca.add_table('buildings', df)


def test_template_validity():
    """
    Run the templates through the standard validation check.
    
    """
    assert validate_template(SaveData)


def test_property_persistence(orca_session):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    pass


def test_csv(orca_session, data):
    """
    Test saving data to a CSV file.
    
    """
    t = SaveData()
    t.table = 'buildings'
    t.output_type = 'csv'
    t.path = 'data/buildings.csv'
    
    t.run()
    
    df = pd.read_csv(t.path).set_index('building_id')
    assert(df.equals(orca.get_table(t.table).to_frame()))
    
    os.remove(t.path)


def test_hdf(orca_session, data):
    """
    Test saving data to an HDF file.
    
    """
    t = SaveData()
    t.table = 'buildings'
    t.output_type = 'hdf'
    t.path = 'data/buildings.h5'
    
    t.run()
    
    df = pd.read_hdf(t.path)
    assert(df.equals(orca.get_table(t.table).to_frame()))
        
    os.remove(t.path)

    
def test_columns(orca_session, data):
    """
    """
    pass


def test_filters(orca_session, data):
    """
    Test applying data filters before table is saved.
    
    """
    t = SaveData()
    t.table = 'buildings'
    t.filters = 'price < 200000'
    t.output_type = 'csv'
    t.path = 'data/buildings.csv'
    
    t.run()
    
    df = pd.read_csv(t.path).set_index('building_id')
    assert(len(df) < 10)
    
    os.remove(t.path)


def test_extra_settings(orca_session, data):
    """
    """
    pass


def test_dynamic_paths(orca_session):
    """
    Test inserting run id, model iteration, or timestamp into path.
    
    """
    t = SaveData()
    t.path = '%RUN%-%ITER%'
    
    assert(t.get_dynamic_filepath() == '0-0')
    
    orca.add_injectable('run_id', 5)
    orca.add_injectable('iter_var', 3)
    
    assert(t.get_dynamic_filepath() == '5-3')
    
    t.path = '%TS%'
    s = t.get_dynamic_filepath()
    assert(len(s) == 15)


