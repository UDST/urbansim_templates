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


TEMPLATE_VERSION = '0.1dev1'

class LargeMultinomialLogitStep(TemplateStep):
    """
    A class for building multinomial logit model steps where the number of alternatives is
    "large". Estimation is performed using choicemodels.MultinomialLogit(). 
    
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
    
    Parameters
    ----------
    choosers : str or list of str, optional
        Name(s) of Orca tables to draw choice scenario data from. The first table is the
        primary one. Any additional tables need to have merge relationships ("broadcasts")
        specified so that they can be merged unambiguously onto the first table. The index
        of the primary table should be a unique ID. In this template, the 'choosers' and
        'alternatives' parameters replace the 'tables' parameter. Both are required for 
        fitting a model, but do not have to be provided when the object is created.
        Reserved column names: <TO DO - fill in>.
    
    alternatives : str or list of str, optional
        Name(s) of Orca tables containing data about alternatives. The first table is the
        primary one. Any additional tables need to have merge relationships ("broadcasts")
        specified so that they can be merged unambiguously onto the first table. The index
        of the primary table should be a unique ID. In this template, the 'choosers' and
        'alternatives' parameters replace the 'tables' parameter. Both are required for 
        fitting a model, but do not have to be provided when the object is created.
        Reserved column names: <TO DO - fill in>.
    
    model_expression : str, optional
        Patsy-style right-hand-side model expression representing the utility of a
        single alternative. Passed to `choicemodels.MultinomialLogit()`. This parameter
        is required for fitting a model, but does not have to be provided when the obect
        is created.
        
    choice_column : str, optional
        Name of the column indicating observed choices, for model estimation. The column
        should contain integers matching the id of the primary `alternatives` table. This
        parameter is required for fitting a model, but it does not have to be provided
        when the object is created. Not required for simulation.
        
    alt_sample_size : int, optional
        Numer of alternatives to sample for each choice scenario. For now, only random 
        sampling is supported. If this parameter is not provided, we will use a sample
        size of one less than the total number of alternatives. (ChoiceModels codebase
        currently requires sampling.)

    chooser_filters : str or list of str, optional
        Filters to apply to the chooser data before fitting the model. These are passed to 
        `pd.DataFrame.query()`. Filters are applied after any additional tables are merged 
        onto the primary one. Replaces the `fit_filters` argument in UrbanSim.

    alt_filters : str or list of str, optional
        Filters to apply to the alternatives data before fitting the model. These are 
        passed to `pd.DataFrame.query()`. Filters are applied after any additional tables 
        are merged onto the primary one. Replaces the `fit_filters` argument in UrbanSim.

    out_choosers : str or list of str, optional
        Name(s) of Orca tables to draw choice scenario data from, for simulation. If not 
        provided, the `choosers` parameter will be used. Same guidance applies.

    out_alternatives : str or list of str, optional
        Name(s) of Orca tables containing data about alternatives, for simulation. If not 
        provided, the `alternatives` parameter will be used. Same guidance applies.

    out_column : str, optional
        Name of the column to write simulated choices to. If it does not already exist
        in the primary `out_choosers` table, it will be created. If not provided, the 
        `choice_column` will be used. Replaces the `out_fname` argument in UrbanSim.
        
        # TO DO - auto-generation not yet working; column must exist.
    
    out_chooser_filters : str or list of str, optional
        Filters to apply to the chooser data before simulation. If not provided, no 
        filters will be applied. Replaces the `predict_filters` argument in UrbanSim.

    out_alt_filters : str or list of str, optional
        Filters to apply to the alternatives data before simulation. If not provided, no 
        filters will be applied. Replaces the `predict_filters` argument in UrbanSim.

    name : str, optional
        Name of the model step, passed to ModelManager. If none is provided, a name is
        generated each time the `fit()` method runs.
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    """
    def __init__(self, choosers=None, alternatives=None, model_expression=None, 
            choice_column=None, alt_sample_size=None, chooser_filters=None, 
            alt_filters=None, out_choosers=None, out_alternatives=None, out_column=None, 
            out_chooser_filters=None, out_alt_filters=None, name=None, tags=[]):
        
        # Parent class can initialize the standard parameters
        TemplateStep.__init__(self, tables=None, model_expression=model_expression, 
                filters=None, out_tables=None, out_column=out_column, out_transform=None, 
                out_filters=None, name=name, tags=tags)

        self.version = TEMPLATE_VERSION
        
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
        LargeMultinomialLogitStep
        
        """
        # Pass values from the dictionary to the __init__() method
        obj = cls(choosers=d['choosers'], alternatives=d['alternatives'], 
            model_expression=d['model_expression'], choice_column=d['choice_column'], 
            alt_sample_size=d['alt_sample_size'], chooser_filters=d['chooser_filters'], 
            alt_filters=d['alt_filters'], out_choosers=d['out_choosers'], 
            out_alternatives=d['out_alternatives'], out_column=d['out_column'], 
            out_chooser_filters=d['out_chooser_filters'], 
            out_alt_filters=d['out_alt_filters'], name=d['name'], tags=d['tags'])

        # Load model fit data
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
        d = {
            'type': self.type,
            'name': self.name,
            'tags': self.tags,
            'choosers': self.choosers,
            'alternatives': self.alternatives,
            'model_expression': self.model_expression,
            'choice_column': self.choice_column,
            'alt_sample_size': self.alt_sample_size,
            'chooser_filters': self.chooser_filters,
            'alt_filters': self.alt_filters,
            'out_choosers': self.out_choosers,
            'out_alternatives': self.out_alternatives,
            'out_column': self.out_column,
            'out_chooser_filters': self.out_chooser_filters,
            'out_alt_filters': self.out_alt_filters,
            'summary_table': self.summary_table,
            'fitted_parameters': self.fitted_parameters,
        }
        return d


    # TO DO - same thing for out_choosers, out_alternatives
    @property
    def choosers(self):
        return self.__choosers
        

    @choosers.setter
    def choosers(self, choosers):
        """
        Normalize storage of the 'choosers' property, which is the name of one or more
        tables that contain data about the choice scenarios (replaces 'tables').
        
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
        Normalize storage of the 'alternatives' property, whis is the name of one or more
        tables that contain data about the alternatives (replaces 'tables').
        
        """
        self.__alternatives = alternatives
        
        if isinstance(alternatives, list):
            # Normalize [] to None
            if len(alternatives) == 0:
                self.__alternatives = None
            
            # Normalize [str] to str
            if len(alternatives) == 1:
                self.__alternatives = alternatives[0]
            
    
    def _get_choosers_df(self):
        """
        Return a single dataframe representing the filtered choosers data.
        
        """
        # TO DO - filter for just the columns we need

        if isinstance(self.choosers, list):
            df = orca.merge_tables(target=self.choosers[0], tables=self.choosers)
        else:
            df = orca.get_table(self.choosers).to_frame()
        
        df = util.apply_filter_query(df, self.chooser_filters)
        return df
        
    
    
    def _get_alternatives_df(self):
        """
        Return a single dataframe representing the filtered alternatives data.
        
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
        Return the number of alternatives to sample. If none is specified, use one less 
        than the number of alternatives
        
        TO DO: The table-merging codebase in ChoiceModels (originally from UrbanSim MNL) 
        currently *requires* sampling of alternatives. We should make it optional.

        """
        if self.alt_sample_size is not None:
            return self.alt_sample_size
        
        else:
            n_minus_1 = len(self._get_alternatives_data()) - 1
            return n_minus_1
    
    
    def fit(self):
        """
        Fit the model; save and report results. This uses the ChoiceModels estimation 
        engine (originally from UrbanSim MNL).
        
        The `fit()` method can be run as many times as desired. Results will not be saved
        with Orca or ModelManager until the `register()` method is run.
        
        """
        # TO DO - update choicemodels to accept a column name for chosen alts
        observations = self._get_choosers_df()
        chosen = observations[self.choice_column]
        
        data = MergedChoiceTable(observations = observations,
                                 alternatives = self._get_alternatives_df(),
                                 chosen_alternatives = chosen,
                                 sample_size = self._get_alt_sample_size())
        
        model = MultinomialLogit(data = data.to_frame(),
                                 observation_id_col = data.observation_id_col, 
                                 choice_col = data.choice_col,
                                 model_expression = self.model_expression)        
        results = model.fit()
        
        self.name = self._generate_name()
        self.summary_table = str(results)
        print(self.summary_table)
        
        # For now, just save the summary table and fitted parameters
        coefs = results.get_raw_results()['fit_parameters']['Coefficient']
        self.fitted_parameters = coefs.tolist()
            
    
    def run(self):
        """
        THIS METHOD DOES NOT WORK YET.
                
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
        to disk so it can be automatically loaded in the future. 
        
        Registering a step will rewrite any previously saved step with the same name. 
        (If a custom name has not been provided, one is generated each time the `fit()` 
        method runs.)
                
        """
        d = self.to_dict()
        mm.add_step(d)

