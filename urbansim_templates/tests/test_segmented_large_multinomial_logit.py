import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models import SegmentedLargeMultinomialLogitStep


@pytest.fixture
def orca_session():
    d1 = {'oid': np.arange(10), 
          'group': np.random.choice(['A','B','C'], size=10),
          'obsval': np.random.random(10),
          'choice': np.random.choice(np.arange(20), size=10)}

    d2 = {'aid': np.arange(20), 
          'altval': np.random.random(20)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


def test_basic_operation(orca_session):
    m = SegmentedLargeMultinomialLogitStep()
    m.defaults.choosers = 'obs'
    m.defaults.alternatives = 'alts'
    m.defaults.choice_column = 'choice'
    m.defaults.model_expression = 'obsval + altval'
    m.segmentation_column = 'group'
    m.fit_all()
    m.to_dict()