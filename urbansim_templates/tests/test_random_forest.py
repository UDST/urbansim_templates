import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models.regression import RandomForestRegressionStep


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

    m = RandomForestRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'b ~ a + c'
    
    m.fit()
	
    m.name = 'random_forest-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('random_forest-test')
    
def test_cross_validate(orca_session):
    """
    Initialize and run cross validation

    Test
    ---------
    Test whether after cross validations validation metrics are added 
    """

    modelmanager.initialize()
    m = modelmanager.get_step('random_forest-test')
    m.cross_validate_score(n_splits=5)

    assert m.cv_metric


def test_simulate(orca_session):
    """
    Fit and run

    Test
    ------------
    Test whether the output variable has been replaced in model.tables
    """
    modelmanager.initialize()
    m = modelmanager.get_step('random_forest-test')

    d1 = orca.get_table(m.tables).to_frame(columns='b')
    m.run()
    d2 = orca.get_table(m.tables).to_frame(columns='b')
    assert ~ d2.equals(d1)


    

