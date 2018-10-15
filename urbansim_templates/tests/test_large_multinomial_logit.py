import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models import LargeMultinomialLogitStep


@pytest.fixture
def orca_session():
    d1 = {'oid': np.arange(10), 
          'obsval': np.random.random(10),
          'choice': np.random.choice(np.arange(20), size=10)}

    d2 = {'aid': np.arange(20), 
          'altval': np.random.random(20)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


def test_observation_sampling(orca_session):
    modelmanager.initialize()

    m = LargeMultinomialLogitStep()
    m.choosers = 'obs'
    m.alternatives = 'alts'
    m.choice_column = 'choice'
    m.model_expression = 'obsval + altval'
    
    m.fit()
    assert(len(m.mergedchoicetable.to_frame()) == 200)
    
    m.chooser_sample_size = 5
    m.fit()
    assert(len(m.mergedchoicetable.to_frame()) == 100)
    
    m.name = 'mnl-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('mnl-test')
    assert(m.chooser_sample_size == 5)
    
    modelmanager.remove_step('mnl-test')


@pytest.fixture
def data():
    num_obs = 100
    num_alts = 120
    
    d1 = {'oid': np.arange(num_obs), 
          'obsval': np.random.random(num_obs),
          'choice': np.random.choice(np.arange(num_alts), size=num_obs)}

    d2 = {'aid': np.arange(num_alts), 
          'altval': np.random.random(num_alts)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


@pytest.fixture
def m(data):
    """
    Build a fitted model.
    
    """
    m = LargeMultinomialLogitStep()
    m.choosers = 'obs'
    m.alternatives = 'alts'
    m.choice_column = 'choice'
    m.model_expression = 'obsval + altval'
    m.alt_sample_size = 10
    
    m.fit()
    return m


def test_property_persistence(m):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    m.fit()
    m.name = 'my-model'
    m.tags = ['tag1']
    m.chooser_filters = 'filters1'
    m.chooser_sample_size = 100
    m.alt_filters = 'filter2'
    m.out_choosers = 'choosers2'
    m.out_alternatives = 'alts2'
    m.out_column = 'choices'
    m.out_chooser_filters = 'filters3'
    m.out_alt_filters = 'filters4'
    m.constrained_choices = True
    m.alt_capacity = 'cap'
    m.chooser_size = 'size'
    m.max_iter = 17
    
    d1 = m.to_dict()
    modelmanager.initialize()
    modelmanager.register(m)
    modelmanager.initialize()
    d2 = modelmanager.get_step('my-model').to_dict()
    
    assert d1 == d2
    modelmanager.remove_step('my-model')
    

def test_simulation_unconstrained(m):
    """
    Test simulation chooser filters with unconstrained choices.
    
    """
    obs = orca.get_table('obs').to_frame()
    obs.loc[:24, 'choice'] = -1
    orca.add_table('obs', obs)
    
    m.out_chooser_filters = 'choice == -1'
    m.run()
    
    assert len(m.choices) == 25
    
    obs = orca.get_table('obs').to_frame()
    assert sum(obs.choice == -1) == 0
    assert obs.loc[:24, 'choice'].equals(m.choices)
    
    
def test_simulation_single_occupancy(m):
    """
    Test simulation of single-occupancy choices.
    
    """
    m.constrained_choices = True
    m.run()
    
    obs = orca.get_table('obs').to_frame()
    assert len(obs) == len(obs.choice.unique())
    
    
def test_simulation_constrained(m):
    """
    Test simulation of choices with explicit capacities and sizes.
    
    """
    obs = orca.get_table('obs').to_frame()
    obs.loc[:,'choice'] = -1
    obs['size'] = np.random.choice([1,2], size=len(obs))
    orca.add_table('obs', obs)
    
    alts = orca.get_table('alts').to_frame()
    alts['cap'] = np.random.choice([1,2,3], size=len(alts))
    orca.add_table('alts', alts)
    
    m.constrained_choices = True
    m.alt_capacity = 'cap'
    m.chooser_size = 'size'
    m.run()
    
    obs = orca.get_table('obs').to_frame()
    assert all(~obs.choice.isin([-1]))

