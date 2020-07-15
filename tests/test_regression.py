import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models import OLSRegressionStep
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    orca.clear_all()
    
    d1 = {'a': np.random.random(100),
          'b': np.random.random(100)}

    obs = pd.DataFrame(d1)
    orca.add_table('obs', obs)


def test_template_validity():
    """
    Run the template through the standard validation check.
    
    """
    assert validate_template(OLSRegressionStep)


def test_ols(orca_session):
    """
    For now this just tests that the code runs.
    
    """
    modelmanager.initialize()

    m = OLSRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'a ~ b'
    
    m.fit()
    
    m.name = 'ols-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('ols-test')
    
    modelmanager.remove_step('ols-test')


def test_simulation(orca_session):
    """
    Test that predicted values are correctly written to Orca.
    
    """
    modelmanager.initialize()
    
    m = OLSRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'a ~ b'
    m.fit()
    
    m.out_column = 'a_predicted'
    m.run()
    
    assert orca.get_table('obs').to_frame()['a_predicted'].equals(m.predicted_values)


def test_out_transform(orca_session):
    """
    Test transformation of the predicted values.
    
    """
    modelmanager.initialize()
    
    m = OLSRegressionStep()
    m.tables = 'obs'
    m.model_expression = 'a ~ b'
    m.fit()
    
    m.out_column = 'a_predicted'
    m.out_transform = 'np.exp'
    m.run()
    
    predictions = m.predicted_values.apply(np.exp)
    
    assert orca.get_table('obs').to_frame()['a_predicted'].equals(predictions)

