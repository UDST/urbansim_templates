from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca
from choicemodels import MultinomialLogit
from choicemodels.tools import MergedChoiceTable
from urbansim.models import MNLDiscreteChoiceModel, util
from urbansim.utils import yamlio

from .shared import TemplateStep
from .. import modelmanager as mm


class LargeMultinomialLogitStep(TemplateStep):
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
    choosers - replaces tables
    alternatives - replaces tables
    model_expression
    (NO model_labels)
    choice_column
    alt_sample_size - NEW
    (NO initial_coefs)
    chooser_filters - replaces filters
    alt_filters - replaces filters

    out_choosers - replaces out_tables 
    out_alternatives - replaces out_tables
    out_column
    out_chooser_filters - replace out_filters
    out_alt_filters - replaces out_filters
    name
    tags
    
    
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
    def __init__(self, choosers=None, alternatives=None, model_expression=None, 
            choice_column=None, alt_sample_size=None, chooser_filters=None, 
            alt_filters=None, out_choosers=None, out_alternatives=None, out_column=None, 
            out_chooser_filters=None, out_alt_filters=None, name=None, tags=[]):
        
        # Parent class can initialize the standard parameters
        TemplateStep.__init__(self, tables=None, model_expression=model_expression, 
                filters=None, out_tables=None, out_column=out_column, out_transform=None, 
                out_filters=None, name=name, tags=tags)

        # Custom parameters not in parent class
        self.choosers = choosers
        self.alternatives = alternatives
        self.choice_column = choice_column
        self.alt_sample_size = alt_sample_size
        self.chooser_filters = chooser_filters
        self.alt_filters = alt_filters
        self.out_choosers = out_choosers
        self.out_alternatives = out_alternatives
        self.out_chooser_filters = out_chooser_filters
        self.out_alt_filters = out_alt_filters
        
        # Placeholders for model fit data, filled in by fit() or from_dict()
        self.summary_table = None 
        self.model = None


#     @classmethod
#     def from_dict(cls, d):
#         """
#         Create an MNLDiscreteChoiceStep object from a saved dictionary representation. (The  
#         resulting object can run() but cannot be fit() again.)
#         
#         Parameters
#         ----------
#         d : dict
#         
#         Returns
#         -------
#         MNLDiscreteChoiceStep
#         
#         """
#         rs = cls(
#             d['model_expression'], sample_size=d['sample_size'], alternatives=d['alternatives'],
#             choosers=d['choosers'], out_fname=d['out_fname'], name=d['name'], tags=d['tags'])
#         rs.type = d['type']
#         
#         # Unpack the urbansim.models.MNLDiscreteChoiceModel() sub-object and resuscitate it
#         model_config = yamlio.convert_to_yaml(d['model'], None)
#         rs.model = MNLDiscreteChoiceModel.from_yaml(model_config)
#         
#         return rs
# 
#     def to_dict(self):
#         """
#         Create a dictionary representation of the object, for input/output.
#         
#         Returns
#         -------
#         dictionary
#         
#         """
#         d = {
#             'type': self.type,
#             'name': self.name,
#             'tags': self.tags,
#             'model_expression': self.model_expression,
#             'choosers': self.choosers,
#             'alternatives': self.alternatives,
#             'sample_size': self.sample_size,
#             'out_fname': self.out_fname,
#             'model': self.model.to_dict()  # urbansim.models.MNLDiscreteChoiceModel() sub-object
#         }
#         return d

    
    # TO DO - same thing for out_choosers, out_alternatives
    @property
    def choosers(self):
        return self.__choosers
        

    @choosers.setter
    def choosers(self, choosers):
        """
        Normalize storage of the 'choosers' property. TO DO - add type validation?
        
        """
        self.__choosers = choosers
        
        if isinstance(choosers, list):
            # Normalize [] to None
            if len(choosers) == 0:
                self.__choosers = None
            
            # Normalize [str] to str
            if len(choosers) == 1:
                self.__choosers = choosers[0]
            
    
    @property
    def alternatives(self):
        return self.__alternatives
        

    @alternatives.setter
    def alternatives(self, alternatives):
        """
        Normalize storage of the 'alternatives' property. TO DO - add type validation?
        
        """
        self.__alternatives = alternatives
        
        if isinstance(alternatives, list):
            # Normalize [] to None
            if len(alternatives) == 0:
                self.__alternatives = None
            
            # Normalize [str] to str
            if len(alternatives) == 1:
                self.__alternatives = alternatives[0]
            
    
    def _get_choosers_data(self):
        """
        Return the ..
        
        """
        # TO DO - filter for just the columns we need

        if isinstance(self.choosers, list):
            df = orca.merge_tables(target=self.choosers[0], tables=self.choosers)
        else:
            df = orca.get_table(self.choosers).to_frame()
        
        df = util.apply_filter_query(df, self.chooser_filters)
        return df
        
    
    
    def _get_alternatives_data(self):
        """
        Return the 
        
        """
        # TO DO - filter for just the columns we need
        
        if isinstance(self.alternatives, list):
            df = orca.merge_tables(target=self.alternatives[0], tables=self.alternatives)
        else:
            df = orca.get_table(self.alternatives).to_frame()
        
        df = util.apply_filter_query(df, self.alt_filters)
        return df
        
    
    def _get_alt_sample_size(self):
        """
        Return the sample size for alternatives. If none specified, use one less than the
        number of alternatives. (TO DO - this is because the table-merging codebase
        doesn't currently support a case without sampling, which needs to be fixed.)
        
        """
        if self.alt_sample_size is not None:
            return self.alt_sample_size
        
        else:
            n_minus_1 = len(self._get_alternatives_data()) - 1
            return n_minus_1
    
    
    def fit(self):
        """
        
        
        """
        # Put together data
        
        # TO DO - update choicemodels to accept a column name for chosen alts
        observations = self._get_choosers_data()
        chosen = observations[self.choice_column]
        
        merged = MergedChoiceTable(observations = observations,
                                   alternatives = self._get_alternatives_data(),
                                   chosen_alternatives = chosen,
                                   sample_size = self._get_alt_sample_size())
        
        # Run model
        model = MultinomialLogit(data = merged.to_frame(),
                                 observation_id_col = merged.observation_id_col, 
                                 choice_col = merged.choice_col,
                                 model_expression = self.model_expression)
        
        results = model.fit()
        print(results)
        
    
    
#     def fit(self, choosers, alternatives, current_choice):
#         """
#         Fit the model; save and report results.
# 
#         """
#         choosers = orca.get_table(choosers).to_frame()
#         alternatives = orca.merge_tables(
#             tables=alternatives, target=alternatives[0])
# 
#         self.model = MNLDiscreteChoiceModel(
#             model_expression=self.model_expression,
#             sample_size=self.sample_size,
#             alts_fit_filters=self.alts_fit_filters,
#             choosers_fit_filters=self.choosers_fit_filters,
#             alts_predict_filters=self.alts_predict_filters,
#             choosers_predict_filters=self.choosers_predict_filters,
#             name=self.name)
# 
#         results = self.model.fit(choosers, alternatives, current_choice)
#         
#         # TO DO: save the results table (as a string?) so we can display it again later
#         print(self.model.report_fit())
        
        
    def run(self):
        """
        Run the model step: calculate predicted values and use them to update a column.
        
        """
        # TO DO: 
        # - Figure out what we can infer about requirements for the underlying data, and
        #   write an 'orca_test' assertion to confirm compliance.
        # - If no destination column was specified, use name of dependent variable

        choosers = orca.get_table(self.choosers).to_frame()
        
        # TO DO - fix to work with single table of alternatives
        alternatives = orca.merge_tables(
            tables=self.alternatives, target=self.alternatives[0])

        values = self.model.predict(choosers, alternatives)
        print("Predicted " + str(len(values)) + " values")
        
        dfw = orca.get_table(self.choosers)
        dfw.update_col_from_series(self.out_fname, values, cast=True)
        
    
    def register(self):
        """
        Register the model step with Orca and the ModelManager. This includes saving it
        to disk so it will be automatically loaded in the future. 
        
        """
        d = self.to_dict()
        mm.add_step(d)