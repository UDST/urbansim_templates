import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models.regression import GradientBoostingRegressionStep

# load rental data
@pytest.fixture
def orca_session():

    d1 = {'a': np.random.random(100),
      'b': np.random.randint(2, size=100),
	  'c': np.random.normal(size=100)}

    obs = pd.DataFrame(d1)
    orca.add_table('obs', obs)

def test_run(orca_session):
    """
    For now this just tests that the code runs.
    
    """
    modelmanager.initialize()

	# gradient boosting
    gb =  GradientBoostingRegressionStep(out_transform=np.exp, out_column='a')
    gb.tables = 'obs'
    gb.n_splits = 10
    gb.model_expression = 'a ~ b + c'
	
    gb.name = 'gb_-test'
   
    gb.fit()
    gb.cross_validate_score()
    modelmanager.register(gb)
    

	