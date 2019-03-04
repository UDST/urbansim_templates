import os

import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import SaveTable
from urbansim_templates.utils import update_column, validate_template


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
    assert validate_template(SaveTable)


def test_property_persistence(orca_session):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    t = SaveTable()
    t.table = 'buildings'
    t.columns = ['window_panes', 'number_of_chimneys']
    t.filters = 'number_of_chimneys > 15'
    t.output_type = 'csv'
    t.path = 'data/buildings.csv'
    t.extra_settings = {'make_data_awesome': True}
    t.name = 'save-buildings-csv'
    t.tags = ['awesome', 'chimneys']
    
    d1 = t.to_dict()
    modelmanager.register(t)
    modelmanager.initialize()
    d2 = modelmanager.get_step(t.name).to_dict()
    
    assert d1 == d2
    modelmanager.remove_step(t.name)


def test_csv(orca_session, data):
    """
    Test saving data to a CSV file.
    
    """
    t = SaveTable()
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
    t = SaveTable()
    t.table = 'buildings'
    t.output_type = 'hdf'
    t.path = 'data/buildings.h5'
    
    t.run()
    
    df = pd.read_hdf(t.path)
    assert(df.equals(orca.get_table(t.table).to_frame()))
        
    os.remove(t.path)

    
def test_columns(orca_session, data):
    """
    Test requesting specific columns.
    
    """
    update_column(table = 'buildings', 
                  column = 'price2', 
                  data = (1e6*np.random.random(10)).astype(int))
    
    t = SaveTable()
    t.table = 'buildings'
    t.columns = 'price2'
    t.output_type = 'csv'
    t.path = 'data/buildings.csv'
    
    t.run()
    
    df = pd.read_csv(t.path).set_index('building_id')
    assert(list(df.columns) == ['price2'])


def test_filters(orca_session, data):
    """
    Test applying data filters before table is saved.
    
    """
    t = SaveTable()
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
    t = SaveTable()
    t.path = '%RUN%-%ITER%'
    
    assert(t.get_dynamic_filepath() == '0-0')
    
    orca.add_injectable('run_id', 5)
    orca.add_injectable('iter_var', 3)
    
    assert(t.get_dynamic_filepath() == '5-3')
    
    t.path = '%TS%'
    s = t.get_dynamic_filepath()
    assert(len(s) == 15)


