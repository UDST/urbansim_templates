from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca
from urbansim.models import MNLDiscreteChoiceModel
from urbansim.utils import yamlio

from .. import modelmanager as mm


class MNLDiscreteChoiceStep(object):
    """
    A class for building discrete choice model steps. This wraps urbansim.models.
    MNLDiscreteChoiceStep() and adds a number of features:
    
    1. Allows passing all parameters needed for the model step at once.
    2. Allows direct registration of the model step with Orca and the ModelManager.
    3. Adds ModelManager metadata: type, name, tags.
    
    Note that the same table and column names are used for both estimation and prediction,
    although the dependent variable may be different if needed. This is in alignment with
    the existing UrbanSim codebase.
    
    Parameters
    ----------
    model_expression : str
        Passed to urbansim.models.MNLDiscreteChoiceModel().
    sample_size : int
        Number of alternatives to randomly sample from for each chooser.
    choosers : str
        Table describing the agents making choices, e.g. households.
    alternatives : str or list of str
        Table describing the things from which agents are choosing,
            e.g. buildings, as well as any broadcast-able tables containing
            relative attributes of the alternatives to be used in fitting
            a choice model
    fit_filters : list of str, optional
        For estimation. Passed to urbansim.models.MNLDiscreteChoiceStep().
    out_fname : str, optional
        For prediction. Name of column to write fitted values to (in the primary table),
        if different from the dependent variable used for estimation.
    predict_filters : list of str, optional
        For prediction. Passed to urbansim.models.MNLDiscreteChoiceStep().
    ytransform : callable, optional
        For prediction. Passed to urbansim.models.MNLDiscreteChoiceStep().
    name : str, optional
        For ModelManager.
    tags : list of str, optional
        For ModelManager.
    
    """

    def __init__(self, model_expression, sample_size, choosers, alternatives, 
            alts_fit_filters=None, choosers_fit_filters=None, out_fname=None,
            alts_predict_filters=None, choosers_predict_filters=None, name=None,
            tags=[]):
        
        self.model_expression = model_expression
        self.sample_size = sample_size
        self.choosers = choosers
        self.alternatives = alternatives
        self.choosers_fit_filters = choosers_fit_filters
        self.alts_fit_filters = alts_fit_filters
        self.out_fname = out_fname
        self.choosers_predict_filters = choosers_predict_filters
        self.alts_predict_filters = alts_predict_filters

        # Placeholder for the MNLDiscreteChoice object, which will be created either in the 
        # fit() method or in the from_dict() class method
        self.model = None

        self.type = 'MNLDiscreteChoiceStep'
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
        Create an MNLDiscreteChoiceStep object from a saved dictionary representation. (The  
        resulting object can run() but cannot be fit() again.)
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        MNLDiscreteChoiceStep
        
        """
        rs = cls(
            d['model_expression'], sample_size=d['sample_size'], alternatives=d['alternatives'],
            choosers=d['choosers'], out_fname=d['out_fname'], name=d['name'], tags=d['tags'])
        rs.type = d['type']
        
        # Unpack the urbansim.models.MNLDiscreteChoiceModel() sub-object and resuscitate it
        model_config = yamlio.convert_to_yaml(d['model'], None)
        rs.model = MNLDiscreteChoiceModel.from_yaml(model_config)
        
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
            'choosers': self.choosers,
            'alternatives': self.alternatives,
            'sample_size': self.sample_size,
            'out_fname': self.out_fname,
            'model': self.model.to_dict()  # urbansim.models.MNLDiscreteChoiceModel() sub-object
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
        tables = list(self.choosers) + self.alternatives
        columns = self.model.columns_used()
        df = orca.merge_tables(target=tables[0], tables=tables, columns=columns)
        return df
    
    def fit(self, choosers, alternatives, current_choice):
        """
        Fit the model; save and report results.

        """
        choosers = orca.get_table(choosers).to_frame()
        alternatives = orca.merge_tables(
            tables=alternatives, target=alternatives[0])

        self.model = MNLDiscreteChoiceModel(
            model_expression=self.model_expression,
            sample_size=self.sample_size,
            alts_fit_filters=self.alts_fit_filters,
            choosers_fit_filters=self.choosers_fit_filters,
            alts_predict_filters=self.alts_predict_filters,
            choosers_predict_filters=self.choosers_predict_filters,
            name=self.name)

        results = self.model.fit(choosers, alternatives, current_choice)
        
        # TO DO: save the results table (as a string?) so we can display it again later
        print(self.model.report_fit())
        
        
    def run(self, choosers, alternatives):
        """
        Run the model step: calculate predicted values and use them to update a column.
        
        """
        # TO DO: 
        # - Figure out what we can infer about requirements for the underlying data, and
        #   write an 'orca_test' assertion to confirm compliance.
        # - If no destination column was specified, use name of dependent variable

        choosers = orca.get_table(choosers).to_frame()
        alternatives = orca.merge_tables(
            tables=alternatives, target=alternatives[0])

        values = self.model.predict(choosers, alternatives)
        print("Predicted " + str(len(values)) + " values")
        
        dfw = orca.get_table(self.choosers)
        dfw.update_col_from_series(self.out_fname, values, cast=True)
        
    
    @classmethod
    def run_from_dict(cls, d):
        """
        Create and run a MNLDiscreteChoiceStep from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        """
        rs = cls.from_dict(d=d)
        rs.run(d['choosers'], d['alternatives'])
      
    
    def register(self):
        """
        Register the model step with Orca and the ModelManager. This includes saving it
        to disk so it will be automatically loaded in the future. 
        
        """
        d = self.to_dict()
        mm.add_step(d)