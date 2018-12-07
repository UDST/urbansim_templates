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
    

def test_colname_validation(orca_session):
    """
    Test for utils.validate_colnames().
    
    """
    tables = ['households', 'buildings']
    model_expression = 'tenure ~ age + pop'
    filters = ['age > 20', 'age < 70']
    extra_columns = 'building_id'
    
    utils.validate_colnames(tables=tables, model_expression=model_expression, 
            filters=filters, extra_columns=None)