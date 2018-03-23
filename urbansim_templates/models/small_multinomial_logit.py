from __future__ import print_function

import numpy as np
import pandas as pd

from choicemodels import MultinomialLogit
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
    - Add support for specifying availability of alternatives
    - Add support for sampling weights
    - Add support for on-the-fly interaction calculations (e.g. distance)
    
    Parameters
    ----------
    tables
        index should be a unique id
        reserved column names: '_obs_id', '_alt_id', '_chosen'
        you can include alts table in the list and it should merge automatically
    model_expression : OrderedDict, optional
    model_labels : OrderedDict, optional
        NEW
    choice_column : str
        NEW - should be ints
    initial_coefs : float, list, or 1D array, optional
        NEW - needs to have length equal to number of parameters being estimated
    filters
    out_tables
    out_column
    out_filters
    name
    tags
    
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
            'choice_column': self.choice_column,
            'initial_coefs': self.initial_coefs,
            'summary_table': self.summary_table
        })
        return d
        
        # TO DO - check that the OrderedDicts are stored properly
        # TO DO - store pickled version of the model
    
    
    def _get_alts(self):
        """
        Get a unique, sorted list of alternative id's included in the model expression.
        
        Returns
        -------
        list
        
        """
        ids = []
        for k, v in self.model_expression.items():
            if isinstance(v, list):
                ids += v
            else:
                ids += [v]
        
        return np.unique(ids)
    
    
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
        Fit the model; save and report results.
        
        """
        long_df = self._to_long(self._get_data())
        
        model = MultinomialLogit(data=long_df, observation_id_col='_obs_id',
                                 choice_col='_chosen',
                                 model_expression=self.model_expression,
                                 model_labels=self.model_labels,
                                 alternative_id_col='_alt_id',
                                 initial_coefs=self.initial_coefs)
        
        results = model.fit()
        print(results.report_fit())
        self.model = results.get_raw_results()


    def run(self):
        """
        
        Only alternatives included in the specification can be chosen.
        
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
        colname = self._get_out_column()
        tabname = self._get_out_table()
        orca.get_table(tabname).update_col_from_series(colname, df._choices, cast=True)


