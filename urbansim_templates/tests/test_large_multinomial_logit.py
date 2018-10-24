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
    assert(len(m.mergedchoicetable.to_frame()) == 190)  # 200 after fixing alt sampling
    
    m.chooser_sample_size = 5
    m.fit()
    assert(len(m.mergedchoicetable.to_frame()) == 95)  # 100 after fixing alt sampling
    
    m.name = 'mnl-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('mnl-test')
    assert(m.chooser_sample_size == 5)
    
    modelmanager.remove_step('mnl-test')
	

