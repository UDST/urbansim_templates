import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager as mm
from urbansim_templates.models import BinaryLogitStep


d1 = {'a': np.random.random(100),
      'b': np.random.randint(2, size=100)}

obs = pd.DataFrame(d1)
orca.add_table('obs', obs)


def test_binary_logit():
    """
    For now this just tests that the code runs.
    
    """
    mm.initialize()

    m = BinaryLogitStep()
    m.tables = 'obs'
    m.model_expression = 'b ~ a'
    
    m.fit()
    
    m.name = 'binary-test'
    m.register()
    
    mm.initialize()
    m = mm.get_step('binary-test')
    
    mm.remove_step('binary-test')