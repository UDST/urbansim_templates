import orca
import pandas as pd
import pytest

from urbansim_templates import utils


def test_parse_version():
    assert utils.parse_version('0.1.0.dev0') == (0, 1, 0, 0)
    assert utils.parse_version('0.115.3') == (0, 115, 3, None)
    assert utils.parse_version('3.1.dev7') == (3, 1, 0, 7)
    assert utils.parse_version('5.4') == (5, 4, 0, None)

def test_version_greater_or_equal():
    assert utils.version_greater_or_equal('2.0', '0.1.1') == True    
    assert utils.version_greater_or_equal('0.1.1', '2.0') == False    
    assert utils.version_greater_or_equal('2.1', '2.0.1') == True
    assert utils.version_greater_or_equal('2.0.1', '2.1') == False
    assert utils.version_greater_or_equal('1.1.3', '1.1.2') == True
    assert utils.version_greater_or_equal('1.1.2', '1.1.3') == False
    assert utils.version_greater_or_equal('1.1.3', '1.1.3') == True
    assert utils.version_greater_or_equal('1.1.3.dev1', '1.1.3.dev0') == True
    assert utils.version_greater_or_equal('1.1.3.dev0', '1.1.3') == False


@pytest.fixture
def orca_session():
    d1 = {'id': [1, 2, 3],
          'building_id': [1, 2, 3],
          'tenure': [1, 1, 0],
          'age': [25, 45, 65]}
    
    d2 = {'building_id': [1, 2, 3],
          'zone_id': [17, 17, 17],
          'pop': [2, 2, 2]}
    
    d3 = {'zone_id': [17],
          'pop': [500]}

    households = pd.DataFrame(d1).set_index('id')
    orca.add_table('households', households)
    
    buildings = pd.DataFrame(d2).set_index('building_id')
    orca.add_table('buildings', buildings)
    
    zones = pd.DataFrame(d3).set_index('zone_id')
    orca.add_table('zones', zones)
    
    orca.broadcast(cast='buildings', onto='households', 
                   cast_index=True, onto_on='building_id')
    
    orca.broadcast(cast='zones', onto='buildings', 
                   cast_index=True, onto_on='zone_id')
    

def test_get_data(orca_session):
    """
    General test - multiple tables, binding filters, extra columns.
        
    """
    df = utils.get_data(tables = ['households', 'buildings'], 
                        model_expression = 'tenure ~ pop', 
                        filters = ['age > 20', 'age < 50'],
                        extra_columns = 'zone_id')
    
    assert(set(df.columns) == set(['tenure', 'pop', 'age', 'zone_id']))
    assert(len(df) == 2)


def test_get_data_single_table(orca_session):
    """
    Single table, no other params.
        
    """
    df = utils.get_data(tables = 'households')
    assert(len(df) == 3)


def test_get_data_bad_columns(orca_session):
    """
    Bad column name, should be ignored.
        
    """
    df = utils.get_data(tables = ['households', 'buildings'], 
                        model_expression = 'tenure ~ pop + potato')
    
    assert(set(df.columns) == set(['tenure', 'pop']))


    
    