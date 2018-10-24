import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models.regression import RandomForestRegressionStep,  GradientBoostingRegressionStep

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

	# random forest
    rf = RandomForestRegressionStep(out_transform=np.exp, out_column='a')
    rf.tables = 'obs'
    rf.n_splits = 10
    rf.model_expression = 'a ~ b + c'
	
    rf.name = 'cross_validate_rf_-test'
   
    rf.fit()
    rf.cross_validate_score()
    
    # gradient boosting
    gb =  GradientBoostingRegressionStep(out_transform=np.exp, out_column='a')
    gb.tables = 'obs'
    gb.n_splits = 10
    gb.model_expression = 'a ~ b + c'
	
    gb.name = 'cross_validate_gb_-test'
    
    
    

	