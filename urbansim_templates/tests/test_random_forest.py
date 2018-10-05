import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models.regression import RandomForestRegressionStep

d1 = {'a': np.random.random(100),
      'b': np.random.randint(2, size=100),
	  'c': np.random.normal(size=100)}

obs = pd.DataFrame(d1)
orca.add_table('obs', obs)


def test_rf():
    """
    For now this just tests that the code runs.
    
    """
    modelmanager.initialize()

    m = RandomForestRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'b ~ a + c'
    
    m.fit()
    m.cross_validate_score()
	
    
    m.name = 'random_forest-test'
    modelmanager.register(m)
    
    #modelmanager.initialize()
    #m = modelmanager.get_step('random_forest-test')
    
	
if __name__ == '__main__':
    test_rf()
	