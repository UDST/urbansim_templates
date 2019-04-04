from __future__ import print_function

import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates.shared import OutputColumnSettings, register_column


def test_property_persistence():
    """
    Confirm OutputColumnSettings properties persist through to_dict() and from_dict().
    
    """
    obj = OutputColumnSettings()
    obj.column_name = 'column'
    obj.table = 'table'
    obj.data_type = 'int32'
    obj.missing_values = 5
    obj.cache = True
    obj.cache_scope = 'iteration'
    
    d = obj.to_dict()
    print(d)
    
    obj2 = OutputColumnSettings.from_dict(d)
    assert(obj2.to_dict() == d)


# Tests for register_column()..

@pytest.fixture
def orca_session():
    """
    Set up a clean Orca session, with a data table.
    
    """
    orca.clear_all()
    
    df = pd.DataFrame({'a': [0.1, 1.33, 2.4]}, index=[1,2,3])
    orca.add_table('tab', df)


def test_column_registration(orca_session):
    """
    Confirm column registration works.
    
    """
    series = pd.Series([4,5,6], index=[1,2,3])
    
    def build_column():
        return series
    
    settings = OutputColumnSettings(column_name='col', table='tab')
    register_column(build_column, settings)
    
    assert(orca.get_table('tab').get_column('col').equals(series))


def test_filling_missing_values(orca_session):
    """
    Confirm that filling missing values works.
    
    """
    series1 = pd.Series([4.0, np.nan, 6.0], index=[1,2,3])
    series2 = pd.Series([4.0, 5.0, 6.0], index=[1,2,3])
    
    def build_column():
        return series1
    
    settings = OutputColumnSettings(column_name='col', table='tab', missing_values=5)
    register_column(build_column, settings)
    
    assert(orca.get_table('tab').get_column('col').equals(series2))


def test_casting_data_type(orca_session):
    """
    Confirm that filling missing values works.
    
    """
    series1 = pd.Series([4.0, 5.0, 6.0], index=[1,2,3])
    series2 = pd.Series([4, 5, 6], index=[1,2,3])
    
    def build_column():
        return series1
    
    settings = OutputColumnSettings(column_name='col', table='tab', data_type='int')
    register_column(build_column, settings)
    
    assert(orca.get_table('tab').get_column('col').equals(series2))


