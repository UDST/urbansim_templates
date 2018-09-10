import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager as mm
from urbansim_templates.models import OLSRegressionStep


d1 = {'a': np.random.random(100),
      'b': np.random.random(100)}

obs = pd.DataFrame(d1)
orca.add_table('obs', obs)


def test_ols():
    """
    For now this just tests that the code runs.
    
    """
    mm.initialize()

    m = OLSRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'a ~ b'
    
    m.fit()
    
    m.name = 'ols-test'
    m.register()
    
    mm.initialize()
    m = mm.get_step('ols-test')
    
    mm.remove_step('ols-test')