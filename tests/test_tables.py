import orca
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.io import Table
from urbansim_templates.utils import validate_template


def test_template_validity():
    """
    Run the template through the standard validation check.
    
    """
    assert validate_template(Table)




