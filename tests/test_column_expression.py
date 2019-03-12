import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import ColumnFromExpression
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca and ModelManager session, with a data table.
    
    """
    orca.clear_all()
    modelmanager.initialize()

    d1 = {'id': np.arange(10), 
          'a': np.random.random(10),
          'b': np.random.choice(np.arange(20), size=10)}

    df = pd.DataFrame(d1).set_index('id')
    orca.add_table('obs', df)


def test_template_validity():
    """
    Check template conforms to basic spec.
    
    """
    assert validate_template(ColumnFromExpression)


def test_run_requirements(orca_session):
    """
    
    
    """
    pass


def test_expression(orca_session):
    """
    Check that column is created correctly.
    
    """
    c = ColumnFromExpression()
    c.column_name = 'c'
    c.table = 'obs'
    c.expression = 'a + sqrt(b)'
    
    c.run()
    series = orca.get_column('obs', 'c')
    print(series)
    

def test_modelmanager_registration(orca_session):
    """
    Check that modelmanager registration and auto-run work as expected.
    
    """
    pass