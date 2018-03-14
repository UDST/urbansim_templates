from __future__ import print_function

import numpy as np
import pandas as pd
import patsy
from datetime import datetime as dt
from statsmodels.api import Logit

import orca

from .shared import TemplateStep
from .. import modelmanager as mm


class BinaryLogitStep(TemplateStep):
    """
    
    This model step type does not support 'out_transform' argument because the output
    is binary values.
    
      
    Is it going to be complicated to handle saving the predicted values? Need to pick some
    data standard, like 1/0
    
    Parameters
    ----------
    tables : str or list of str
    model_expression : str
    filters : str or list of str, optional
        Replaces `fit_filters` argument.
    out_tables : str or list of str, optional
    out_column : str, optional
        Replaces `out_fname` argument.
    out_filters : str or list of str, optional
        Replaces `predict_filters` argument.
    name : str, optional
        For ModelManager.
    tags : list of str, optional
        For ModelManager.
    
    """
    def __init__(self, tables=None, model_expression=None, filters=None, out_tables=None,
            out_column=None, out_transform=None, out_filters=None, name=None, tags=None):
        
        TemplateStep.__init__(self, tables=tables, model_expression=model_expression, 
                filters=filters, out_tables=out_tables, out_column=out_column, 
                out_filters=out_filters, name=name, tags=tags)
        
        self.summary_table = None  # placeholder
        self.fitted_parameters = None  # placeholder
        
    
    def fit(self):
        """
        Fit the model; save and report results.
        
        """
        # TO DO - verify that params are in place for estimation
        
        m = Logit.from_formula(data=self._get_data(), formula=self.model_expression)
        results = m.fit()
        
        self.summary_table = results.summary()
        print(self.summary_table)
        
        # For now, we can just save the summary table and the fitted parameters. Later on
        # we will probably want programmatic access to more details about the fit (e.g. 
        # for autospec), but we can add that when it's needed.      
        
        self.fitted_parameters = results.params.tolist()  # params is a pd.Series
        
    
    def predict(self):
        """
        Generate predicted values and save them to the specified Orca location. 
        
        For binary logit, we calculate predicted predicted probabilities and then do a 
        weighted random draw to determine the binary outcomes.
        
        TO DO - how to handle more complicated actions? Like for move-out we need to do
        some data management. 
        
        """
        # TO DO - verify that params are in place for prediction
        
        dm = patsy.dmatrices(data=self._get_data('predict'),
                             formula_like=self.model_expression,
                             return_type='dataframe')[1]
        
        beta_X = np.dot(dm, self.fitted_parameters)
        probs = np.divide(np.exp(beta_X), 1 + np.exp(beta_X))
        
        rand = np.random.random(len(probs))
        choices = np.less(rand, probs)
        
        return choices
        
        
        