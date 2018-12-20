from __future__ import print_function

import numpy as np
import pandas as pd
import patsy
from datetime import datetime as dt
from statsmodels.api import Logit

import orca

from .. import modelmanager
from .shared import TemplateStep


@modelmanager.template
class BinaryLogitStep(TemplateStep):
    """
    A class for building binary logit model steps. This extends TemplateStep, where some
    common functionality is defined. Estimation is handled by Statsmodels and simulation
    is handled within this class.
    
    Expected usage:
    - create a model object
    - specify some parameters
    - run the `fit()` method
    - iterate as needed
    
    Then, for simulation:
    - specify some simulation parameters
    - use the `run()` method for interactive testing
    - use `modelmanager.register()` to save the model to Orca and disk
    - registered steps can be accessed via ModelManager and Orca
    
    All parameters listed in the constructor can be set directly on the class object,
    at any time.
    
    Parameters
    ----------
    tables : str or list of str, optional
        Name(s) of Orca tables to draw data from. The first table is the primary one. 
        Any additional tables need to have merge relationships ("broadcasts") specified
        so that they can be merged unambiguously onto the first table. Among them, the 
        tables must contain all variables used in the model expression and filters. The
        left-hand-side variable should be in the primary table. The `tables` parameter is 
        required for fitting a model, but it does not have to be provided when the object 
        is created.

    model_expression : str, optional
        Patsy formula containing both the left- and right-hand sides of the model
        expression: http://patsy.readthedocs.io/en/latest/formulas.html
        This parameter is required for fitting a model, but it does not have to be 
        provided when the object is created.

    filters : str or list of str, optional
        Filters to apply to the data before fitting the model. These are passed to 
        `pd.DataFrame.query()`. Filters are applied after any additional tables are merged 
        onto the primary one. Replaces the `fit_filters` argument in UrbanSim.
    
    out_tables : str or list of str, optional
        Name(s) of Orca tables to use for simulation. If not provided, the `tables` 
        parameter will be used. Same guidance applies: the tables must be able to be 
        merged unambiguously, and must include all columns used in the right-hand-side
        of the model expression and in the `out_filters`.
    
    out_column : str, optional
        Name of the column to write simulated choices to. If it does not already exist
        in the primary output table, it will be created. If not provided, the left-hand-
        side variable from the model expression will be used. Replaces the `out_fname` 
        argument in UrbanSim.
        
        # TO DO - auto-generation not yet working; column must exist in the primary table
    
    out_filters : str or list of str, optional
        Filters to apply to the data before simulation. If not provided, no filters will
        be applied. Replaces the `predict_filters` argument in UrbanSim.
        
    out_value_true : numeric or str, optional
        Value to save to the output column corresponding to an affirmative choice. 
        Default is 1 (int). Use keyword 'nothing' to leave values unchanged.
    
    out_value_false : numeric or str, optional
        Value to save to the output column corresponding to a negative choice. Default 
        is 0 (int). Use keyword 'nothing' to leave values unchanged.
    
    name : str, optional
        Name of the model step, passed to ModelManager. If none is provided, a name is
        generated each time the `fit()` method runs.
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    """
    def __init__(self, tables=None, model_expression=None, filters=None, out_tables=None,
            out_column=None, out_filters=None, out_value_true=1, out_value_false=0, 
            name=None, tags=[]):
        
        # Parent class can initialize the standard parameters
        TemplateStep.__init__(self, tables=tables, model_expression=model_expression, 
                filters=filters, out_tables=out_tables, out_column=out_column, 
                out_transform=None, out_filters=out_filters, name=name, tags=tags)
        
        # Custom parameters not in parent class
        self.out_value_true = out_value_true
        self.out_value_false = out_value_false
        
        # Placeholders for model fit data, filled in by fit() or from_dict()
        self.summary_table = None 
        self.fitted_parameters = None
        
    
    @classmethod
    def from_dict(cls, d):
        """
        Create an object instance from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        BinaryLogitStep
        
        """
        # Pass values from the dictionary to the __init__() method
        obj = cls(tables=d['tables'], model_expression=d['model_expression'], 
                filters=d['filters'], out_tables=d['out_tables'], 
                out_column=d['out_column'], out_filters=d['out_filters'], 
                out_value_true=d['out_value_true'], out_value_false=d['out_value_false'], 
                name=d['name'], tags=d['tags'])
                
        obj.summary_table = d['summary_table']
        obj.fitted_parameters = d['fitted_parameters']
        
        return obj
    
    
    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Returns
        -------
        dict
        
        """
        d = TemplateStep.to_dict(self)
        
        # Add parameters not in parent class
        d.update({
            'out_value_true': self.out_value_true,
            'out_value_false': self.out_value_false,
            'summary_table': self.summary_table,
            'fitted_parameters': self.fitted_parameters
        })
        return d
    
    
    def fit(self):
        """
        Fit the model; save and report results. This currently uses the Statsmodels
        Logit class with default estimation settings. (It will shift to ChoiceModels
        once more infrastructure is in place.)
        
        The `fit()` method can be run as many times as desired. Results will not be saved 
        with Orca or ModelManager until the `register()` method is run. 
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        """
        # TO DO - verify that params are in place for estimation
        
        # Workaround for a temporary statsmodels bug: 
        # https://github.com/statsmodels/statsmodels/issues/3931
        from scipy import stats
        stats.chisqprob = lambda chisq, df: stats.chi2.sf(chisq, df)

        m = Logit.from_formula(data=self._get_data(), formula=self.model_expression)
        results = m.fit()

        self.name = self._generate_name()        
        self.summary_table = str(results.summary())
        print(self.summary_table)
        
        # For now, we can just save the summary table and the fitted parameters. Later on
        # we will probably want programmatic access to more details about the fit (e.g. 
        # for autospec), but we can add that when it's needed.      
        
        self.fitted_parameters = results.params.tolist()  # params is a pd.Series
        
    
    def run(self):
        """
        Run the model step: calculate simulated choices and use them to update a column.
        
        For binary logit, we calculate predicted probabilities and then perform a weighted 
        random draw to determine the simulated binary outcomes. This is done directly from 
        the fitted parameters, because we can't conveniently regenerate a Statsmodels 
        results object from a dictionary representation.
        
        The predicted probabilities and simulated choices are saved to the class object 
        for interactive use (`probabilities` and `choices`, with type pd.Series) but are 
        not persisted in the dictionary representation of the model step.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        """
        # TO DO - verify that params are in place for prediction
        
        df = self._get_data('predict')
        
        dm = patsy.dmatrices(data=df, formula_like=self.model_expression,
                             return_type='dataframe')[1]  # right-hand-side design matrix
        
        beta_X = np.dot(dm, self.fitted_parameters)
        probs = np.divide(np.exp(beta_X), 1 + np.exp(beta_X))
        
        rand = np.random.random(len(probs))
        choices = np.less(rand, probs)
        
        # Save results to the class object (via df to include index)
        df['_probs'] = probs
        self.probabilities = df._probs
        df['_choices'] = choices
        self.choices = df._choices
                
        # TO DO - generate column if it does not exist

        colname = self._get_out_column()
        tabname = self._get_out_table()
        
        if self.out_value_true != 'nothing':
            df.loc[df._choices==True, colname] = self.out_value_true
        
        if self.out_value_false != 'nothing':
            df.loc[df._choices==False, colname] = self.out_value_false
        
        orca.get_table(tabname).update_col_from_series(colname, df[colname], cast=True)
        
        