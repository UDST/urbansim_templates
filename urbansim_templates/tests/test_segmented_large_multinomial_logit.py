import numpy as np
import pandas as pd
import pytest

import orca
from urbansim.models.util import apply_filter_query

from urbansim_templates import modelmanager
from urbansim_templates.models import SegmentedLargeMultinomialLogitStep


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca session with a couple of data tables.
    
    """
    d1 = {'oid': np.arange(100), 
          'group': np.random.choice(['A','B','C'], size=100),
          'int_group': np.random.choice([3,4], size=100),
          'obsval': np.random.random(100),
          'choice': np.random.choice(np.arange(20), size=100)}

    d2 = {'aid': np.arange(20), 
          'altval': np.random.random(20)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


@pytest.fixture
def m(orca_session):
    """
    Set up a partially configured model step.
    
    """
    m = SegmentedLargeMultinomialLogitStep()
    m.defaults.choosers = 'obs'
    m.defaults.alternatives = 'alts'
    m.defaults.choice_column = 'choice'
    m.defaults.model_expression = 'obsval + altval'
    m.segmentation_column = 'group'
    return m


def test_basic_operation(m):
    """
    Test basic operation of the template.
    
    """
    m.fit_all()
    m.to_dict()
    assert len(m.submodels) == 3
    
    
def test_numeric_segments(m):
    """
    Test support for using ints as categorical variables.
    
    """
    m.segmentation_column = 'int_group'
    m.build_submodels()
    assert len(m.submodels) == 2
    

def test_chooser_filters(m):
    """
    Test that the default chooser filters generate the correct data subset.
    
    """
    m.defaults.chooser_filters = "group != 'A'"
    m.build_submodels()
    assert len(m.submodels) == 2 

    m.defaults.chooser_filters = ["group != 'A'", "group != 'B'"]
    m.build_submodels()
    assert len(m.submodels) == 1


def test_alternative_filters(m):
    """
    Test that the default alternative filters generate the correct data subset.
    
    """
    m.defaults.alt_filters = 'aid < 5'
    
    df = orca.get_table(m.defaults.choosers).to_frame()
    len1 = len(df.loc[df.choice < 5])
    len2 = len(m.get_segmentation_column())
    
    assert len1 == len2


def test_submodel_filters(m):
    """
    Test that submodel filters generate the correct data subset.
    
    """
    m.build_submodels()
    
    df = orca.get_table(m.defaults.choosers).to_frame()
    len1 = len(apply_filter_query(df.loc[df.group == 'A'], m.defaults.chooser_filters))
    len2 = len(apply_filter_query(df, m.submodels['A'].chooser_filters))
    
    assert len1 == len2
    

def test_property_persistence(m):
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
    

def test_filter_generation(m):
    """
    Test additional cases of generating submodel filters.
    
    """
    m.defaults.chooser_filters = 'obsval > 0.5'
    m.build_submodels()
    assert m.submodels['A'].chooser_filters == ['obsval > 0.5', "group == 'A'"]
    
    m.defaults.chooser_filters = ['obsval > 0.5', 'obsval < 0.9']
    m.build_submodels()
    assert m.submodels['A'].chooser_filters == \
                ['obsval > 0.5', 'obsval < 0.9', "group == 'A'"]
    

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


