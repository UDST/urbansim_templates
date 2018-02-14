from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca
from urbansim.models import RegressionModel
from urbansim.utils import yamlio

from extensions import modelmanager as mm


class RegressionStep(object):
    """
    A class for building regression model steps. This wraps urbansim.models.
    RegressionModel() and adds a number of features:
    
    1. Allows passing all parameters needed for the model step at once.
    2. Allows direct registration of the model step with Orca and the ModelManager.
    3. Adds ModelManager metadata: type, name, tags.
    
    Note that the same table and column names are used for both estimation and prediction,
    although the dependent variable may be different if needed. This is in alignment with
    the existing UrbanSim codebase.
    
    Parameters
    ----------
    model_expression : str
        Passed to urbansim.models.RegressionModel().
    tables : str or list of str
        Name(s) of Orca tables to draw data from. The first table is the primary one.
        Any additional tables need to have merge relationships ("broadcasts") specified
        so that they can be merged unambiguously onto the first table. 
    fit_filters : list of str, optional
        For estimation. Passed to urbansim.models.RegressionModel().
    out_fname : str, optional
        For prediction. Name of column to write fitted values to (in the primary table),
        if different from the dependent variable used for estimation.
    predict_filters : list of str, optional
        For prediction. Passed to urbansim.models.RegressionModel().
    ytransform : callable, optional
        For prediction. Passed to urbansim.models.RegressionModel().
    name : str, optional
        For ModelManager.
    tags : list of str, optional
        For ModelManager.
    
    """
    def __init__(self, model_expression, tables, fit_filters=None, out_fname=None,    
            predict_filters=None, ytransform=None, name=None, tags=[]):
        
        self.model_expression = model_expression
        self.tables = tables
        self.fit_filters = fit_filters
        self.out_fname = out_fname
        self.predict_filters = predict_filters
        self.ytransform = ytransform

        # Placeholder for the RegressionModel object, which will be created either in the 
        # fit() method or in the from_dict() class method
        self.model = None
        
        self.type = 'RegressionStep'
        self.name = name
        self.tags = tags
        
        # Generate a name if none provided - TO DO: maybe this should be the time of 
        # model fitting rather than the time the object is created, in order to be 
        # consistent with the regression results that print?
        if (self.name == None):
            self.name = self.type + '-' + dt.now().strftime('%Y%m%d-%H%M%S')
    
        # TO DO: 
        # - Figure out what we can infer about requirements for the underlying data, and
        #   write an 'orca_test' assertion to confirm compliance.

    
    @classmethod
    def from_dict(cls, d):
        """
        Create a RegressionStep object from a saved dictionary representation. (The  
        resulting object can run() but cannot be fit() again.)
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        RegressionStep
        
        """
        rs = cls(d['model_expression'], d['tables'], out_fname=d['out_fname'], 
                name=d['name'], tags=d['tags'])
        rs.type = d['type']
        
        # Unpack the urbansim.models.RegressionModel() sub-object and resuscitate it
        model_config = yamlio.convert_to_yaml(d['model'], None)
        rs.model = RegressionModel.from_yaml(model_config)
        
        return rs
        
    
    def to_dict(self):
        """
        Create a dictionary representation of the object, for input/output.
        
        Returns
        -------
        dictionary
        
        """
        d = {
            'type': self.type,
            'name': self.name,
            'tags': self.tags,
            'model_expression': self.model_expression,
            'tables': self.tables,
            'out_fname': self.out_fname,
            'model': self.model.to_dict()  # urbansim.models.RegressionModel() sub-object
        }
        return d
        
        
    def get_data(self):
        """
        Generate a data table for estimation or prediction, from Orca table and column
        names. The results should not be stored, in case the data in Orca changes.
        
        Returns
        -------
        DataFrame
        
        """
        # TO DO: handle single table as well as list
        tables = self.tables
        columns = self.model.columns_used()
        df = orca.merge_tables(target=tables[0], tables=tables, columns=columns)
        return df
    
    
    def fit(self):
        """
        Fit the model; save and report results.
        
        """
        self.model = RegressionModel(model_expression=self.model_expression,
                fit_filters=self.fit_filters, predict_filters=self.predict_filters,
                ytransform=self.ytransform, name=self.name)

        results = self.model.fit(self.get_data())
        
        # TO DO: save the results table (as a string?) so we can display it again later
        print(results.summary())
        
        
    def run(self):
        """
        Run the model step: calculate predicted values and use them to update a column.
        
        """
        # TO DO: 
        # - Figure out what we can infer about requirements for the underlying data, and
        #   write an 'orca_test' assertion to confirm compliance.
        # - If no destination column was specified, use name of dependent variable

        values = self.model.predict(self.get_data())
        print("Predicted " + str(len(values)) + " values")
        
        dfw = orca.get_table(self.tables[0])
        dfw.update_col_from_series(self.out_fname, values, cast=True)
        
    
    @classmethod
    def run_from_dict(cls, d):
        """
        Create and run a RegressionStep from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        """
        rs = cls.from_dict(d)
        rs.run()
      
    
    def register(self):
        """
        Register the model step with Orca and the ModelManager. This includes saving it
        to disk so it will be automatically loaded in the future. 
        
        """
        d = self.to_dict()
        mm.add_step(d)
        
        
        
        
        