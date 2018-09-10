import orca
import numpy as np
import pandas as pd
import pytest
from collections import OrderedDict

from urbansim_templates import modelmanager as mm
from urbansim_templates.models import SmallMultinomialLogitStep


d1 = {'a': np.random.random(100),
      'b': np.random.random(100),
      'choice': np.random.randint(3, size=100)}

obs = pd.DataFrame(d1)
orca.add_table('obs', obs)


def test_small_mnl():
    """
    For now this just tests that the code runs.
    
    """
    mm.initialize()

    m = SmallMultinomialLogitStep()
    m.tables = 'obs'
    m.choice_column = 'choice'
    m.model_expression = OrderedDict([
            ('intercept', [1,2]), ('a', [0,2]), ('b', [0,2])])
    
    m.fit()
    
    m.name = 'small-mnl-test'
    m.register()
    
    mm.initialize()
    m = mm.get_step('small-mnl-test')
    
    mm.remove_step('small-mnl-test')