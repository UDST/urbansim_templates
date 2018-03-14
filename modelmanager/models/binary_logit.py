from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca

from .shared import TemplateStep
from .. import modelmanager as mm


class BinaryLogitStep(TemplateStep):
    """
    
      
    Is it going to be complicated to handle saving the predicted values? Need to pick some
    data standard, like 1/0
    
    Parameters
    ----------
    tables : str or list of str
    model_expression : str
    filters : str or list of str ?, optional
        Replaces `fit_filters` argument.
    out_tables : str or list of str, optional
    out_column : str, optional
        Replaces `out_fname` argument.
    out_transform : callable, optional
        Replaces `ytransform` argument.
    out_filters : str or list of str ?, optional
        Replaces `predict_filters` argument.
    name : str, optional
        For ModelManager.
    tags : list of str, optional
        For ModelManager.
    
    """
    def __init__(self, tables, model_expression, filters=None, out_tables=None,
            out_column=None, out_transform=None, out_filters=None, name=None, tags=None):
        
        TemplateStep.__init__(self, tables, model_expression, filters, out_tables, 
                out_column, out_transform, out_filters, name, tags)
        
        self.type = 'BinaryLogitStep'
        
        
        