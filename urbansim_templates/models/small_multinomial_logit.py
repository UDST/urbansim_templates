from __future__ import print_function

import numpy as np
import pandas as pd

import orca

from .shared import TemplateStep
from .. import modelmanager as mm


class SmallMultinomialLogitStep(TemplateStep):
    """
    A class for building multinomial logit model steps where the number of alternatives is
    "small". Estimation is handled by ChoiceModels and PyLogit. Simulation is handled by
    PyLogit and within this class. 
    
    Multinomial Logit models can involve a range of different specification and estimation
    mechanics. For now these are separated into two templates. What's the difference?
    
    "Small" MNL:
    - data is in a single table (choosers)
    - each alternative can have a different model expression
    - all the alternatives are available to all choosers
    - estimation and simulation use the PyLogit engine (via ChoiceModels)
    
    "Large" MNL:
    - data is in two tables (choosers and alternatives)
    - each alternative has the same model expression
    - N alternatives are sampled for each chooser
    - estimation and simulation use the ChoiceModels engine (formerly UrbanSim MNL)
    
    TO DO:
    - Add support for sampling weights
    - Add support for on-the-fly interaction calculations (e.g. distance)
    - Add support for special columns in the choosers table for things like availability 
      of alternatives or alternative-specific data values? Not sure we need this on top of
      model expressions that vary by alternative. But we could implement it pretty easily
      using PyLogit's `choicetools.convert_wide_to_long()`.
    
    Parameters
    ----------
    tables
    model_expression : OrderedDict, optional
    model_labels : OrderedDict, optional
        NEW
    choice_col : str
        NEW
    initial_coefs : float, list, or 1D array, optional
        NEW
    filters
    out_tables
    out_column
    out_filters
    name
    tags
    
    """
    def __init__(self, tables=None, model_expression=None, model_labels=None,
            choice_col=None, initial_coefs=None, filters=None, out_tables=None,
            out_column=None, out_filters=None, name=None, tags=[]):
        
        # Parent class can initialize the standard parameters
        TemplateStep.__init__(self, tables=tables, model_expression=model_expression, 
                filters=filters, out_tables=out_tables, out_column=out_column, 
                out_transform=None, out_filters=out_filters, name=name, tags=tags)
        
        # Custom parameters not in parent class
        self.model_labels = model_labels
        self.choice_col = choice_col
        self.initial_coefs = initial_coefs
        
        # Placeholders for model fit data, filled in by fit() or from_dict()
        self.summary_table = None 
        self.model = None

    
    @classmethod
    def from_dict(cls, d):
        """
        Create an object instance from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        SmallMultinomialLogitStep
        
        """
        # TO DO - FILL THIS IN
        
        # Pass values from the dictionary to the __init__() method
        obj = cls(tables=d['tables'], model_expression=d['model_expression'], 
                filters=d['filters'], out_tables=d['out_tables'], 
                out_column=d['out_column'], out_filters=d['out_filters'], 
                out_value_true=d['out_value_true'], out_value_false=d['out_value_false'], 
                name=d['name'], tags=d['tags'])
                
        obj.summary_table = d['summary_table']
        obj.fitted_parameters = d['fitted_parameters']
        
        return obj
        
        # TO DO - check that this is re-creating OrderedDicts properly
        # TO DO - read pickled version of the model


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
            'model_labels': self.model_labels,
            'choice_col': self.choice_col,
            'initial_coefs': self.initial_coefs,
            'summary_table': self.summary_table
        })
        return d
        
        # TO DO - check that the OrderedDicts are stored properly
        # TO DO - store pickled version of the model
    
    
    def fit(self):
        """
        Fit the model; save an report results.
        
        """
        # Get column names out of OrderedDict
        
        # Get data
        
        # Convert to long format
        
        # Pass to ChoiceModels
        
        # Save the underlying model


    def run(self):
        """
        
        """
        # Get predictions from underlying model
        
        # Save them to Orca







