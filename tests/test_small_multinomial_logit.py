import orca
import numpy as np
import pandas as pd
import pytest
from collections import OrderedDict

from urbansim_templates import modelmanager
from urbansim_templates.models import SmallMultinomialLogitStep
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    orca.clear_all()

    d1 = {'id': np.arange(100),
          'building_id': np.arange(100),
          'a': np.random.random(100),
          'choice': np.random.randint(3, size=100)}
    
    d2 = {'building_id': np.arange(100),
          'b': np.random.random(100)}

    households = pd.DataFrame(d1).set_index('id')
    orca.add_table('households', households)
    
    buildings = pd.DataFrame(d2).set_index('building_id')
    orca.add_table('buildings', buildings)

    orca.broadcast(cast='buildings', onto='households', 
                   cast_index=True, onto_on='building_id')


def test_template_validity():
    """
    Run the template through the standard validation check.
    
    """
    assert validate_template(SmallMultinomialLogitStep)


def test_small_mnl(orca_session):
    """
    Test that the code runs, and that the model_expression is always available.
    
    """
    modelmanager.initialize()

    m = SmallMultinomialLogitStep()
    m.tables = ['households', 'buildings']
    m.choice_column = 'choice'
    m.model_expression = OrderedDict([
            ('intercept', [1,2]), ('a', [0,2]), ('b', [0,2])])
    
    m.fit()
    assert(m.model_expression is not None)
    
    print(m.model_expression)
    
    m.name = 'small-mnl-test'
    modelmanager.register(m)
    assert(m.model_expression is not None)
    
    print(m.model_expression)
    
    # TEST SIMULATION
    m.out_column = 'simulated_choice'
    
    m.run()
    print(orca.get_table('households').to_frame())
    
    modelmanager.initialize()
    m = modelmanager.get_step('small-mnl-test')
    assert(m.model_expression is not None)
    
    print(m.model_expression)
    
    modelmanager.remove_step('small-mnl-test')