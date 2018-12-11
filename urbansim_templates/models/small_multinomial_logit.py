from __future__ import print_function

from collections import OrderedDict
import os
import pickle

import numpy as np
import pandas as pd

from choicemodels import MultinomialLogit
import orca

from .. import modelmanager
from .shared import TemplateStep


@modelmanager.template
class SmallMultinomialLogitStep(TemplateStep):
    """
    A class for building multinomial logit model steps where the number of alternatives is
    "small". Estimation is handled by PyLogit via the ChoiceModels API. Simulation is 
    handled by PyLogit (probabilities) and ChoiceModels (simulation draws). 
    
    Multinomial logit models can involve a range of different specification and estimation
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
    - Add support for specifying availability of alternatives
    - Add support for sampling weights
    - Add support for on-the-fly interaction calculations (e.g. distance)
    
    Parameters
    ----------
    tables : str or list of str, optional
        Name(s) of Orca tables to draw data from. The first table is the primary one. 
        Any additional tables need to have merge relationships ("broadcasts") specified
        so that they can be merged unambiguously onto the first table. Among them, the 
        tables must contain all variables used in the model expression and filters. The
        index of the primary table should be a unique ID. The `tables` parameter is 
        required for fitting a model, but it does not have to be provided when the object 
        is created. Reserved column names: '_obs_id', '_alt_id', '_chosen'.

    model_expression : OrderedDict, optional
        PyLogit model expression. This parameter is required for fitting a model, but it 
        does not have to be provided when the object is created.
    
    model_labels : OrderedDict, optional
        PyLogit model labels.
        
    choice_column : str, optional
        Name of the column indicating observed choices, for model estimation. The column
        should contain integers matching the alternatives in the model expression. This
        parameter is required for fitting a model, but it does not have to be provided
        when the object is created.
        
    initial_coefs : list of numerics, optional
        Starting values for the parameter estimation algorithm, passed to PyLogit. Length 
        must be equal to the number of parameters being estimated. If this is not 
        provided, zeros will be used.
        
    filters : str or list of str, optional
        Filters to apply to the data before fitting the model. These are passed to 
        `pd.DataFrame.query()`. Filters are applied after any additional tables are merged 
        onto the primary one. Replaces the `fit_filters` argument in UrbanSim.

    out_tables : str or list of str, optional
        Name(s) of Orca tables to use for simulation. If not provided, the `tables` 
        parameter will be used. Same guidance applies: the tables must be able to be 
        merged unambiguously, and must include all columns used in the model expression 
        and in the `out_filters`.

    out_column : str, optional
        Name of the column to write simulated choices to. If it does not already exist
        in the primary output table, it will be created. If not provided, the 
        `choice_column` will be used. Replaces the `out_fname` argument in UrbanSim.
        
        # TO DO - auto-generation not yet working; column must exist in the primary table

    out_filters : str or list of str, optional
        Filters to apply to the data before simulation. If not provided, no filters will
        be applied. Replaces the `predict_filters` argument in UrbanSim.
        
    name : str, optional
        Name of the model step, passed to ModelManager. If none is provided, a name is
        generated each time the `fit()` method runs.
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    """
    def __init__(self, tables=None, model_expression=None, model_labels=None,
            choice_column=None, initial_coefs=None, filters=None, out_tables=None,
            out_column=None, out_filters=None, name=None, tags=[]):
        
        # Parent class can initialize the standard parameters
        TemplateStep.__init__(self, tables=tables, model_expression=model_expression, 
                filters=filters, out_tables=out_tables, out_column=out_column, 
                out_transform=None, out_filters=out_filters, name=name, tags=tags)
        
        # Custom parameters not in parent class
        self.model_labels = model_labels
        self.choice_column = choice_column
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
        # Pass values from the dictionary to the __init__() method
        obj = cls(tables=d['tables'], model_expression=None, model_labels=None, 
                choice_column=d['choice_column'], initial_coefs=d['initial_coefs'], 
                filters=d['filters'], out_tables=d['out_tables'], 
                out_column=d['out_column'], out_filters=d['out_filters'], name=d['name'], 
                tags=d['tags'])
                
        # Load non-strings and model fit parameters
        # TO DO - handle non-existence cases more carefully than 'except pass'!
        try:
            k = d['model_expression_keys']
            v = d['model_expression_values']
            obj.model_expression = OrderedDict([(k[i], v[i]) for i in range(len(k))])
        except:
            pass

        try:
            k = d['model_label_keys']
            v = d['model_label_values']
            obj.model_labels = OrderedDict([(k[i], v[i]) for i in range(len(k))])
        except:
            pass
                
        obj.summary_table = d['summary_table']
        
        if 'supplemental_objects' in d:
            for item in filter(None, d['supplemental_objects']):
                if (item['name'] == 'model-object'):
                    obj.model = item['content']
        
        return obj


    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Returns
        -------
        dict
        
        """
        tmp_model_expression = self.model_expression
        self.model_expression = None
        
        d = TemplateStep.to_dict(self)
        self.model_expression = tmp_model_expression
        
        # Can't store OrderedDicts in YAML, so convert them
        if tmp_model_expression is not None:
            d.update({
                'model_expression_keys': [k for (k,v) in tmp_model_expression.items()],
                'model_expression_values': [v for (k,v) in tmp_model_expression.items()],
            })
            
        if self.model_labels is not None:
            d.update({
                'model_label_keys': [k for (k,v) in self.model_labels.items()],
                'model_label_values': [v for (k,v) in self.model_labels.items()]
            })
        
        # Add parameters not in parent class
        d.update({
            'model_labels': None,
            'choice_column': self.choice_column,
            'initial_coefs': self.initial_coefs,
            'summary_table': self.summary_table
        })
        
        # Add supplemental objects
        objects = []
        if self.model is not None:
            objects.append({'name': 'model-object',
                            'content': self.model,
                            'content_type': 'pickle',
                            'required': True})

        d.update({'supplemental_objects': objects})
        
        return d
    
    
    def _get_alts(self):
        """
        Get a unique, sorted list of alternative id's included in the model expression.
        
        Returns
        -------
        list
        
        """
        ids = []
        for k, v in self.model_expression.items():
            # TO DO - check if PyLogit supports v being a non-list (single numeric) 
            for elem in v:
                if isinstance(elem, list):
                    ids += elem
                else:
                    ids += [elem]
        
        return np.unique(ids)
    
    
    def _get_param_count(self):
        """
        Count the number of parameters implied by the model expression.
        
        Returns
        -------
        int
        
        """
        count = 0
        for k, v in self.model_expression.items():
            # TO DO - check if PyLogit supports v being a non-list (single numeric) 
            for elem in v:
                count += 1
        
        return count
    
    
    def _to_long(self, df, task='fit'):
        """
        Convert a data table from wide format to long format. Currently handles the case
        where there are attributes of choosers but not of alternatives, and no 
        availability or interaction terms. (This is not supported in the PyLogit 
        conversion utility.)
                
        TO DO 
        - extend to handle characteristics of alternatives?
        - move to ChoiceModels
        
        Parameters
        ----------
        df : pd.DataFrame
            One row per observation. The observation id should be in the index. Reserved 
            column names: '_obs_id', '_alt_id', '_chosen'.
        
        task : 'fit' or 'predict', optional
            If 'fit' (default), a column named '_chosen' is generated with binary 
            indicator of observed choices.
            
        Returns
        -------
        pd.DataFrame
            One row per combination of observation and alternative. The observation is in 
            '_obs_id'. The alternative is in 'alt_id'. Table is sorted by observation and 
            alternative. If task is 'fit', a column named '_chosen' is generated with 
            binary indicator of observed choices. Remaining columns are retained from the 
            input data.
        
        """
        # Get lists of obs and alts
        obs = df.index.sort_values().unique().tolist()
        alts = self._get_alts()
        
        # Long df is cartesian product of alts and obs
        obs_prod, alts_prod = pd.core.reshape.util.cartesian_product([obs, alts])

        long_df = pd.DataFrame({'_obs_id': obs_prod, '_alt_id': alts_prod})
        long_df = long_df.merge(df, left_on='_obs_id', right_index=True)
        
        if (task == 'fit'):
            # Add binary indicator of chosen rows
            long_df['_chosen'] = 0
            long_df.loc[long_df._alt_id == long_df[self.choice_column], '_chosen'] = 1

        return long_df    
    
    
    def fit(self):
        """
        Fit the model; save and report results. This uses PyLogit via ChoiceModels.
        
        The `fit()` method can be run as many times as desired. Results will not be saved 
        with Orca or ModelManager until the `register()` method is run. 
        
        """
        long_df = self._to_long(self._get_data())
        
        # Set initial coefs to 0 if none provided
        pc = self._get_param_count()
        if (self.initial_coefs is None) or (len(self.initial_coefs) != pc):
            self.initial_coefs = np.zeros(pc).tolist()

        model = MultinomialLogit(data=long_df, observation_id_col='_obs_id',
                                 choice_col='_chosen',
                                 model_expression=self.model_expression,
                                 model_labels=self.model_labels,
                                 alternative_id_col='_alt_id',
                                 initial_coefs=self.initial_coefs)
        
        results = model.fit()

        self.name = self._generate_name()        
        self.summary_table = str(results.report_fit())
        print(self.summary_table)

        # We need the PyLogit fitted model object for prediction, so save it directly
        self.model = results.get_raw_results()


    def run(self):
        """
        Run the model step: calculate simulated choices and use them to update a column.
        
        Alternatives that appear in the estimation data but not in the model expression
        will not be available for simulation.
        
        Predicted probabilities come from PyLogit. Monte Carlo simulation of choices is
        performed directly. (This functionality will move to ChoiceModels.)
        
        The predicted probabilities and simulated choices are saved to the class object 
        for interactive use (`probabilities` with type pd.DataFrame, and `choices` with 
        type pd.Series) but are not persisted in the dictionary representation of the 
        model step.
        
        """
        df = self._get_data('predict')
        long_df = self._to_long(df, 'predict')
        
        num_obs = len(df)
        num_alts = len(self._get_alts())
        
        # Get predictions from underlying model - this is an ndarray with the same length
        # as the long-format df, representing choice probability for each alternative
        probs = self.model.predict(long_df)
        
        # Generate choices by adapting an approach from UrbanSim MNL
        # https://github.com/UDST/choicemodels/blob/master/choicemodels/mnl.py#L578-L583
        cumprobs = probs.reshape((num_obs, num_alts)).cumsum(axis=1)
        rands = np.random.random(num_obs)
        diff = np.subtract(cumprobs.transpose(), rands).transpose()
        
        # The diff conversion replaces negative values with 0 and positive values with 1,
        # so that argmax can return the position of the first positive value
        choice_ix = np.argmax((diff + 1.0).astype('i4'), axis=1)
        choice_ix_1d = choice_ix + (np.arange(num_obs) * num_alts)
        
        choices = long_df._alt_id.values.take(choice_ix_1d)
                
        # Save results to the class object (via df to include indexes)
        long_df['_probability'] = probs
        self.probabilities = long_df[['_obs_id', '_alt_id', '_probability']]
        df['_choices'] = choices
        self.choices = df._choices
       
        # Save to Orca
        if self.out_column is not None:
            colname = self.out_column
        else:
            colname = self.choice_column

        tabname = self._get_out_table()
        orca.get_table(tabname).update_col_from_series(colname, df._choices, cast=True)

