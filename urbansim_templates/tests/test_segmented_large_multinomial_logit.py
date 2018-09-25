import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models import SegmentedLargeMultinomialLogitStep


@pytest.fixture
def orca_session():
    d1 = {'oid': np.arange(10), 
          'group': np.random.choice(['A','B','C'], size=10),
          'obsval': np.random.random(10),
          'choice': np.random.choice(np.arange(20), size=10)}

    d2 = {'aid': np.arange(20), 
          'altval': np.random.random(20)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


@pytest.fixture
def m(orca_session):
    m = SegmentedLargeMultinomialLogitStep()
    m.defaults.choosers = 'obs'
    m.defaults.alternatives = 'alts'
    m.defaults.choice_column = 'choice'
    m.defaults.model_expression = 'obsval + altval'
    m.segmentation_column = 'group'
    return m


def test_basic_operation(m):
    m.fit_all()
    m.to_dict()
    assert len(m.submodels) == 3
    
    
def test_numeric_segments(m):
    """
    Test support for ints as categorical variables.
    
    """
    pass
    

def test_filtering(m):
    """
    Test that submodel filters are applied correctly.
    
    
    """
    pass
    

def test_persistence(m):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    m.name = 'test'
    m.tags = ['one','two']
    m.fit_all()
    d1 = m.to_dict()
    modelmanager.initialize()
    modelmanager.register(m)
    modelmanager.initialize()
    d2 = modelmanager.get_step('test').to_dict()
    assert d1 == d2
    modelmanager.remove_step('test')
    

def test_filtering(m):
    """
    Test additional cases of transforming submodel filters.
    
    """
    m.defaults.chooser_filters = 'test-string'
    m.build_submodels()
    assert m.submodels['A'].chooser_filters == ['test-string', "group == 'A'"]
    
    m.defaults.chooser_filters = ['t1', 't2']
    m.build_submodels()
    assert m.submodels['A'].chooser_filters == ['t1', 't2', "group == 'A'"]
    

@pytest.fixture
def d():
    d = {'choosers': 'a', 
         'alternatives': 'b', 
         'model_expression': 'c', 
         'choice_column': 'd', 
         'chooser_sample_size': 'f', 
         'alt_filters': 'g', 
         'alt_sample_size': 'h', 
         'out_choosers': 'i', 
         'out_alternatives': 'j', 
         'out_column': 'k', 
         'out_chooser_filters': 'l',
         'out_alt_filters': 'm'}
    return d    


def test_initial_propagation_of_defaults(m):
    """
    Test that submodels receive properties of the defaults object.
    
    """    
    d = m.defaults.to_dict()
    
    m.build_submodels()

    d2 = m.submodels['A'].to_dict()
    for k, v in d.items():
        if k != 'chooser_filters':
            assert d2[k] == v


def test_subsequent_propagation_of_defaults(m, d):
    """
    Test that submodels are updated correctly when the defaults are subsequently changed.
    
    """
    m.build_submodels()
    
    for k, v in d.items():
        setattr(m.defaults, k, v)

    d2 = m.submodels['A'].to_dict()
    for k, v in d.items():
        assert d2[k] == v
    
    # chooser_filters should NOT be passed to the submodels
    m.defaults.chooser_filters = 'test'
    assert m.submodels['A'].chooser_filters != 'test'


def test_independence_of_submodels(m, d):
    """
    Test that updating one submodel does not change others.
    
    """
    m.build_submodels()
    
    for k, v in d.items():
        setattr(m.submodels['A'], k, v)

    d2 = m.submodels['B'].to_dict()
    for k, v in d.items():
        assert d2[k] != v




