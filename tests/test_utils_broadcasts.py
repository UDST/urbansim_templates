import pandas as pd
import pytest

import orca

from urbansim_templates.utils import validate_table


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca session.
    
    """
    orca.clear_all()


def test_validation_index_unique(orca_session):
    """
    Table validation should pass if the index is unique.
    
    These tests of the validate() method generate Orca tables directly, which is just a 
    shortcut for testing -- the intended use is for the method to validate the table
    loaded by the TableStep. 
    
    """
    d = {'id': [1,2,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index('id'))
    
    validate_table('tab')
    

def test_validation_index_not_unique(orca_session):
    """
    Table validation should raise a ValueError if the index is not unique.
    
    """
    d = {'id': [1,1,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index('id'))
    
    try:
        validate_table('tab')
    except ValueError:
        return
    
    pytest.fail()  # fail if ValueError wasn't raised


def test_validation_multiindex_unique(orca_session):
    """
    Table validation should pass with a MultiIndex whose combinations are unique.
    
    """
    d = {'id': [1,1,1], 'sub_id': [1,2,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index(['id', 'sub_id']))
    
    validate_table('tab')


def test_validation_multiindex_not_unique(orca_session):
    """
    Table validation should raise a ValueError if the MultiIndex combinations are not 
    unique.
    
    """
    d = {'id': [1,1,1], 'sub_id': [2,2,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d).set_index(['id', 'sub_id']))
    
    try:
        validate_table('tab')
    except ValueError:
        return
    
    pytest.fail()  # fail if ValueError wasn't raised


def test_validation_unnamed_index(orca_session):
    """
    Table validation should raise a ValueError if index is unnamed.
    
    """
    d = {'id': [1,1,3], 'value': [4,4,4]}
    orca.add_table('tab', pd.DataFrame(d))  # generates auto index without a name
    
    try:
        validate_table('tab')
    except ValueError:
        return
    
    pytest.fail()  # fail if ValueError wasn't raised
    

def test_validation_columns_vs_other_indexes(orca_session):
    """
    Table validation should compare the 'households.building_id' column to 
    'buildings.build_id'.
    
    """
    d = {'household_id': [1,2,3], 'building_id': [2,3,4]}
    orca.add_table('households', pd.DataFrame(d).set_index('household_id'))

    d = {'building_id': [1,2,3,4], 'value': [4,4,4,4]}
    orca.add_table('buildings', pd.DataFrame(d).set_index('building_id'))

    validate_table('households')


def test_validation_index_vs_other_columns(orca_session):
    """
    Table validation should compare the 'households.building_id' column to 
    'buildings.build_id'.
    
    """
    d = {'building_id': [1,2,3,4], 'value': [4,4,4,4]}
    orca.add_table('buildings', pd.DataFrame(d).set_index('building_id'))

    d = {'household_id': [1,2,3], 'building_id': [2,3,5]}
    orca.add_table('households', pd.DataFrame(d).set_index('household_id'))

    validate_table('buildings')


def test_validation_with_multiindexes(orca_session):
    """
    Here, table validation should compare 'choice_table.[home_tract,work_tract]' to
    'distances.[home_tract,work_tract]'.
    
    """
    d = {'obs_id': [1,1,1,1], 'alt_id': [1,2,3,4], 
         'home_tract': [55,55,55,55], 'work_tract': [17,46,19,55]}
    orca.add_table('choice_table', pd.DataFrame(d).set_index(['obs_id','alt_id']))

    d = {'home_tract': [55,55,55], 'work_tract': [17,18,19], 'dist': [1,1,1]}
    orca.add_table('distances', pd.DataFrame(d).set_index(['home_tract','work_tract']))

    validate_table('choice_table')

