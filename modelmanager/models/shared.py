from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca

from .. import modelmanager as mm


class TemplateStep(object):
    """
    Shared functionality for the template classes.
    
    """
    def __init__(self, tables, model_expression, filters=None, out_tables=None,
                 out_column=None, out_transform=None, out_filters=None, name=None,
                 tags=None):
        
        self.tables = tables
        self.model_expression = model_expression
        self.filters = filters
        
        self.out_tables = out_tables
        self.out_column = out_column
        self.out_transform = out_transform
        self.out_filters = out_filters
        
        self.name = name
        self.tags = tags
        self.type = 'TemplateStep'
        
        # Placeholder for the fitted model
        self.model = None
        
        # It seems fine for users to access and change the above properties directly.
        # If we want to test for acceptable values, a good way to do it would be with
        # @property definitions.
