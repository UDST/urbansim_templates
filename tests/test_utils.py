import numpy as np
import pandas as pd
import pytest

import orca

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


###############################
## get_df

@pytest.fixture
def df():
    d = {'id': [1,2,3], 'val1': [4,5,6], 'val2': [7,8,9]}
    return pd.DataFrame(d).set_index('id')


def test_get_df_dataframe(df):
    """
    Confirm that get_df() works when passed a DataFrame.
    
    """
    df_out = utils.get_df(df)
    pd.testing.assert_frame_equal(df, df_out)
    

def test_get_df_str(df):
    """
    Confirm that get_df() works with str input.
    
    """
    orca.add_table('df', df)
    df_out = utils.get_df('df')
    pd.testing.assert_frame_equal(df, df_out)


def test_get_df_dataframewrapper(df):
    """
    Confirm that get_df() works with orca.DataFrameWrapper input.
    
    """
    dfw = orca.DataFrameWrapper('df', df)
    df_out = utils.get_df(dfw)
    pd.testing.assert_frame_equal(df, df_out)    
    

def test_get_df_tablefuncwrapper(df):
    """
    Confirm that get_df() works with orca.TableFuncWrapper input.
    
    """
    def df_callable():
        return df
    
    tfw = orca.TableFuncWrapper('df', df_callable)
    df_out = utils.get_df(tfw)
    pd.testing.assert_frame_equal(df, df_out)    
    

def test_get_df_columns(df):
    """
    Confirm that get_df() limits columns, and filters out duplicates and invalid ones.
    
    """
    dfw = orca.DataFrameWrapper('df', df)
    df_out = utils.get_df(dfw, ['id', 'val1', 'val1', 'val3'])
    pd.testing.assert_frame_equal(df[['val1']], df_out)    
    

def test_get_df_unsupported_type(df):
    """
    Confirm that get_df() raises an error for an unsupported type.
    
    """
    try:
        df_out = utils.get_df([df])
    except ValueError as e:
        print(e)
        return
    
    pytest.fail()
    


###############################
## all_cols

def test_all_cols_dataframe(df):
    """
    Confirm that all_cols() works with DataFrame input.
    
    """
    cols = utils.all_cols(df)
    assert sorted(cols) == sorted(['id', 'val1', 'val2'])


def test_all_cols_orca(df):
    """
    Confirm that all_cols() works with Orca input.
    
    """
    orca.add_table('df', df)
    cols = utils.all_cols('df')
    assert sorted(cols) == sorted(['id', 'val1', 'val2'])


def test_all_cols_extras(df):
    """
    Confirm that all_cols() includes columns not part of the Orca core table.
    
    """
    orca.add_table('df', df)
    orca.add_column('df', 'newcol', pd.Series())
    cols = utils.all_cols('df')
    assert sorted(cols) == sorted(['id', 'val1', 'val2', 'newcol'])


def test_all_cols_unsupported_type(df):
    """
    Confirm that all_cols() raises an error for an unsupported type.
    
    """
    try:
        cols = utils.all_cols([df])
    except ValueError as e:
        print(e)
        return
    
    pytest.fail()




###############################
## get_data

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


def test_update_column(orca_session):
    """
    General test.
    
    Additional tests to add: series without index, adding column on the fly.
    
    """
    table = 'buildings'
    column = 'pop'
    data = pd.Series([3,3,3], index=[1,2,3])
    
    utils.update_column(table, column, data)
    assert(orca.get_table(table).to_frame()[column].tolist() == [3,3,3])
    
    
def test_update_column_incomplete_series(orca_session):
    """
    Update certain values but not others, with non-matching index orders.
    
    """
    table = 'buildings'
    column = 'pop'
    data = pd.Series([10,5], index=[3,1])
    
    utils.update_column(table, column, data)
    assert(orca.get_table(table).to_frame()[column].tolist() == [5,2,10])
    

def test_add_column_incomplete_series(orca_session):
    """
    Add an incomplete column to confirm that it's aligned based on the index. (The ints 
    will be cast to floats to accommodate the missing values.)
    
    """
    table = 'buildings'
    column = 'pop2'
    data = pd.Series([10,5], index=[3,1])
    
    utils.update_column(table, column, data)
    stored_data = orca.get_table(table).to_frame()[column].tolist()
    
    np.testing.assert_array_equal(stored_data, [5.0, np.nan, 10.0])
