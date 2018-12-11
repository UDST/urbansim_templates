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
    d1 = {'a': np.random.random(100),
          'b': np.random.random(100),
          'choice': np.random.randint(3, size=100)}

    obs = pd.DataFrame(d1)
    orca.add_table('obs', obs)


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
    m.tables = 'obs'
    m.choice_column = 'choice'
    m.model_expression = OrderedDict([
            ('intercept', [1,2]), ('a', [0,2]), ('b', [0,2])])
    
    m.fit()
    assert(m.model_expression is not None)
    
    m.name = 'small-mnl-test'
    modelmanager.register(m)
    assert(m.model_expression is not None)
    
    modelmanager.initialize()
    m = modelmanager.get_step('small-mnl-test')
    assert(m.model_expression is not None)
    
    modelmanager.remove_step('small-mnl-test')