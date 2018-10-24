import pytest
import orca
import numpy as np
import pandas as pd

from urbansim_templates import utils
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor

@pytest.fixture
def orca_session():

    d1 = {'a': np.random.random(100),
      'b': np.random.randint(2, size=100),
	  'c': np.random.normal(size=100)}

    obs = pd.DataFrame(d1)
    orca.add_table('obs', obs)

def test_version_parse():
    assert utils.version_parse('0.1.0.dev0') == (0, 1, 0, 0)
    assert utils.version_parse('0.115.3') == (0, 115, 3, None)
    assert utils.version_parse('3.1.dev7') == (3, 1, 0, 7)
    assert utils.version_parse('5.4') == (5, 4, 0, None)

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

def test_convert_to_model(orca_session):
    """
    Create a model from sklearn and transform it into a urbansim_templates models

    Test
    ------------------
    Check wether model.fit, model.predict have dataframe as argument after conversion

    """
    d1 = orca.get_table('obs')

    rf = RandomForestRegressor()
    rf_new = utils.convert_to_model(rf, ' a ~ b + c')

    rf_new.fit(d1)
    rf_new.predict(d1)

def test_fit_keywords(orca_session):
    """
    Create a model from sklearn and transform it into a urbansim_templates models

    Test
    ------------------
    Check wether keywords in the original fit method are transfered to model.fit

    """
    d1 = orca.get_table('obs')

    rf = RandomForestRegressor()
    rf_new = utils.convert_to_model(rf, 'a ~ b + c')

    weights = np.ones(len(d1))
    rf_new.fit(d1, sample_weight=weights) 


def test_parsing(orca_session):
    """
    From a model expression in patsy format, extract corresponding columns from a data

    Test
    -------------------------------------
    test whether from_patsy_to_array returns df['a'] and df[['b', 'c']] from 'a ~ b + c'

    """
    d = orca.get_table('obs').to_frame()
    d_x, d_y = utils.from_patsy_to_array('a ~ b + c', d)

    assert (d_x == d[['b', 'c']]).all().all()
    assert d_y.equals(d[['a']])

def test_parsing_transform(orca_session):
    """
    From a model expression in patsy format, extract corresponding columns from a data

    Test
    -------------------------------------
    test whether from_patsy_to_array returns df['np.exp(a)'] and df[[np.log1p(np.exp(b)), 'c']] 
    from 'np.exp(a) ~ np.log1p(np.exp(b))+ c'

    """
    d = orca.get_table('obs').to_frame()
    d_x, d_y = utils.from_patsy_to_array('np.exp(a) ~ np.log1p(np.exp(b)) + c', d)

    assert (d_x.columns == ['np.log1p(np.exp(b))', 'c']).all()
    assert d_y.columns == ['np.exp(a)']


def test_parsing_space(orca_session):
    """
    From a model expression in patsy format, extract corresponding columns from a data
    after patsy cleans the expression by removing extra space
    Test
    -------------------------------------
    test whether from_patsy_to_array returns df['a'] and df[['b', 'c']] from ' a ~ b + c'

    """
    d = orca.get_table('obs').to_frame()
    d_x, d_y = utils.from_patsy_to_array(' a ~ b + c', d)

    assert (d_x == d[['b', 'c']]).all().all()
    assert d_y.equals(d[['a']])
