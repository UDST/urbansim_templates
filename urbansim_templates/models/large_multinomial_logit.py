from __future__ import print_function

import numpy as np
import pandas as pd
import patsy

import orca
from choicemodels import mnl
from choicemodels import MultinomialLogit
from choicemodels.tools import MergedChoiceTable

from .. import modelmanager
from .shared import TemplateStep


@modelmanager.template
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
        Reserved column names: 'chosen', 'join_index', 'observation_id'.
    
    alternatives : str or list of str, optional
        Name(s) of Orca tables containing data about alternatives. The first table is the
        primary one. Any additional tables need to have merge relationships ("broadcasts")
        specified so that they can be merged unambiguously onto the first table. The index
        of the primary table should be a unique ID. In this template, the 'choosers' and
        'alternatives' parameters replace the 'tables' parameter. Both are required for 
        fitting a model, but do not have to be provided when the object is created.
        Reserved column names: 'chosen', 'join_index', 'observation_id'.
    
    model_expression : str, optional
        Patsy-style right-hand-side model expression representing the utility of a
        single alternative. Passed to `choicemodels.MultinomialLogit()`. This parameter
        is required for fitting a model, but does not have to be provided when the object
        is created.
        
    choice_column : str, optional
        Name of the column indicating observed choices, for model estimation. The column
        should contain integers matching the id of the primary `alternatives` table. This
        parameter is required for fitting a model, but it does not have to be provided
        when the object is created. Not required for simulation.
        
    chooser_filters : str or list of str, optional
        Filters to apply to the chooser data before fitting the model. These are passed to 
        `pd.DataFrame.query()`. Filters are applied after any additional tables are merged 
        onto the primary one. Replaces the `fit_filters` argument in UrbanSim.

    chooser_sample_size : int, optional
        Number of choosers to sample, for faster model fitting. Sampling is random and may 
        vary between model runs.

    alt_filters : str or list of str, optional
        Filters to apply to the alternatives data before fitting the model. These are 
        passed to `pd.DataFrame.query()`. Filters are applied after any additional tables 
        are merged onto the primary one. Replaces the `fit_filters` argument in UrbanSim.
        Choosers whose chosen alternative is removed by these filters will not be included
        in the model estimation.

    alt_sample_size : int, optional
        Numer of alternatives to sample for each choice scenario. For now, only random 
        sampling is supported. If this parameter is not provided, we will use a sample
        size of one less than the total number of alternatives. (ChoiceModels codebase
        currently requires sampling.) The same sample size is used for estimation and
        prediction.

    out_choosers : str or list of str, optional
        Name(s) of Orca tables to draw choice scenario data from, for simulation. If not 
        provided, the `choosers` parameter will be used. Same guidance applies. Reserved 
        column names: 'chosen', 'join_index', 'observation_id'.

    out_alternatives : str or list of str, optional
        Name(s) of Orca tables containing data about alternatives, for simulation. If not 
        provided, the `alternatives` parameter will be used. Same guidance applies. 
        Reserved column names: 'chosen', 'join_index', 'observation_id'.

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
            choice_column=None, chooser_filters=None, chooser_sample_size=None,
            alt_filters=None, alt_sample_size=None, out_choosers=None, 
            out_alternatives=None, out_column=None, out_chooser_filters=None, 
            out_alt_filters=None, name=None, tags=[]):
        
        self._listeners = []
        
        # Parent class can initialize the standard parameters
        TemplateStep.__init__(self, tables=None, model_expression=model_expression, 
                filters=None, out_tables=None, out_column=out_column, out_transform=None, 
                out_filters=None, name=name, tags=tags)

        # Custom parameters not in parent class
        self.choosers = choosers
        self.alternatives = alternatives
        self.choice_column = choice_column
        self.chooser_filters = chooser_filters
        self.chooser_sample_size = chooser_sample_size
        self.alt_filters = alt_filters
        self.alt_sample_size = alt_sample_size
        self.out_choosers = out_choosers
        self.out_alternatives = out_alternatives
        self.out_chooser_filters = out_chooser_filters
        self.out_alt_filters = out_alt_filters
        
        # Placeholders for model fit data, filled in by fit() or from_dict()
        self.summary_table = None 
        self.fitted_parameters = None


    def bind_to(self, callback):
        self._listeners.append(callback)
    
    
    def send_to_listeners(self, param, value):
        for callback in self._listeners:
            callback(param, value)
    
    
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
            chooser_filters=d['chooser_filters'], 
            chooser_sample_size=d['chooser_sample_size'],
            alt_filters=d['alt_filters'], alt_sample_size=d['alt_sample_size'], 
            out_choosers=d['out_choosers'], out_alternatives=d['out_alternatives'], 
            out_column=d['out_column'], out_chooser_filters=d['out_chooser_filters'], 
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
            'template': self.template,
            'template_version': self.template_version,
            'name': self.name,
            'tags': self.tags,
            'choosers': self.choosers,
            'alternatives': self.alternatives,
            'model_expression': self.model_expression,
            'choice_column': self.choice_column,
            'chooser_filters': self.chooser_filters,
            'chooser_sample_size': self.chooser_sample_size,
            'alt_filters': self.alt_filters,
            'alt_sample_size': self.alt_sample_size,
            'out_choosers': self.out_choosers,
            'out_alternatives': self.out_alternatives,
            'out_column': self.out_column,
            'out_chooser_filters': self.out_chooser_filters,
            'out_alt_filters': self.out_alt_filters,
            'summary_table': self.summary_table,
            'fitted_parameters': self.fitted_parameters,
        }
        return d


    # TO DO - there has got to be a less verbose way to handle getting and setting
    
    @property
    def choosers(self):
        return self.__choosers
    @choosers.setter
    def choosers(self, value):
        self.__choosers = self._normalize_table_param(value)
        self.send_to_listeners('choosers', value)
            
    @property
    def alternatives(self):
        return self.__alternatives
    @alternatives.setter
    def alternatives(self, value):
        self.__alternatives = self._normalize_table_param(value)
        self.send_to_listeners('alternatives', value)
    
    @property
    def model_expression(self):
        return self.__model_expression
    @model_expression.setter
    def model_expression(self, value):
        self.__model_expression = value
        self.send_to_listeners('model_expression', value)
    
    @property
    def choice_column(self):
        return self.__choice_column
    @choice_column.setter
    def choice_column(self, value):
        self.__choice_column = value
        self.send_to_listeners('choice_column', value)
    
    @property
    def chooser_filters(self):
        return self.__chooser_filters
    @chooser_filters.setter
    def chooser_filters(self, value):
        self.__chooser_filters = value
        self.send_to_listeners('chooser_filters', value)
            
    @property
    def chooser_sample_size(self):
        return self.__chooser_sample_size
    @chooser_sample_size.setter
    def chooser_sample_size(self, value):
        self.__chooser_sample_size = value
        self.send_to_listeners('chooser_sample_size', value)
            
    @property
    def alt_filters(self):
        return self.__alt_filters
    @alt_filters.setter
    def alt_filters(self, value):
        self.__alt_filters = value
        self.send_to_listeners('alt_filters', value)

    @property
    def alt_sample_size(self):
        return self.__alt_sample_size
    @alt_sample_size.setter
    def alt_sample_size(self, value):
        self.__alt_sample_size = value
        self.send_to_listeners('alt_sample_size', value)

    @property
    def out_choosers(self):
        return self.__out_choosers
    @out_choosers.setter
    def out_choosers(self, value):
        self.__out_choosers = self._normalize_table_param(value)
        self.send_to_listeners('out_choosers', value)
            
    @property
    def out_alternatives(self):
        return self.__out_alternatives
    @out_alternatives.setter
    def out_alternatives(self, value):
        self.__out_alternatives = self._normalize_table_param(value)            
        self.send_to_listeners('out_alternatives', value)
    
    @property
    def out_column(self):
        return self.__out_column
    @out_column.setter
    def out_column(self, value):
        self.__out_column = value
        self.send_to_listeners('out_column', value)
            
    @property
    def out_chooser_filters(self):
        return self.__out_chooser_filters
    @out_chooser_filters.setter
    def out_chooser_filters(self, value):
        self.__out_chooser_filters = value
        self.send_to_listeners('out_chooser_filters', value)
            
    @property
    def out_alt_filters(self):
        return self.__out_alt_filters
    @out_alt_filters.setter
    def out_alt_filters(self, value):
        self.__out_alt_filters = value
        self.send_to_listeners('out_alt_filters', value)
            
            
    def _get_alt_sample_size(self):
        """
        Return the number of alternatives to sample. If none is specified, use one less 
        than the number of alternatives. 
        
        (This is a temporary solution to the problem that the table-merging codebase in 
        ChoiceModels currently _requires_ sampling of alternatives. We should make it 
        optional.)
        
        TO DO: What if `out_alternatives` is smaller than `alternatives`? What if it's
        smaller than `alt_sample_size`?

        """
        if self.alt_sample_size is not None:
            return self.alt_sample_size
        
        else:
            alternatives = self._get_df(tables = self.alternatives, 
                                        filters = self.alt_filters)
            
            n_minus_1 = len(alternatives) - 1
            return n_minus_1
    
    
    def fit(self, mct=None):
        """
        Fit the model; save and report results. This uses the ChoiceModels estimation 
        engine (originally from UrbanSim MNL).
        
        The `fit()` method can be run as many times as desired. Results will not be saved
        with Orca or ModelManager until the `register()` method is run.
        
        After sampling alternatives for each chooser, the merged choice table is saved to 
        the class object for diagnostic use (`mergedchoicetable` with type
        choicemodels.tools.MergedChoiceTable).
        
        Parameters
        ----------
        mct : choicemodels.tools.MergedChoiceTable
            This parameter is a temporary backdoor allowing us to pass in a more 
            complicated merged choice table than can be generated within the template, for
            example including sampling weights or interaction terms. This will work for 
            model estimation, but is not yet hooked up to the prediction functionality.
        
        Returns
        -------
        None
        
        """
        if (mct is not None):
            data = mct
            
        else:        
            # TO DO - update choicemodels to accept a column name for chosen alts
            observations = self._get_df(tables=self.choosers, 
                                        filters=self.chooser_filters)
        
            if (self.chooser_sample_size is not None):
                observations = observations.sample(self.chooser_sample_size)
            
            chosen = observations[self.choice_column]
        
            alternatives = self._get_df(tables = self.alternatives, 
                                        filters = self.alt_filters)
        
            data = MergedChoiceTable(observations = observations,
                                     alternatives = alternatives,
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
        
        # Save merged choice table to the class object for diagnostic use
        self.mergedchoicetable = data
            
    
    def _get_chosen_ids(self, ids, positions):
        """
        Inconveniently, `choicemodels.mnl.mnl_simulate()` identifies choices by position
        rather than id. This function converts them. It should move to ChoiceModels.
        
        We observe N choice scenarios. In each, one of J alternatives is chosen. We have a 
        long (len N * J) list of the available alternatives. We have a list (len N) of 
        which alternatives were chosen, but it identifies them by POSITION and we want 
        their ID.    
    
        Parameters
        ----------
        ids : list or list-like
            List of alternative ID's (len N * J).
        
        positions : list or list-like
            List of chosen alternatives by position (len N), where each entry is
            an int in range [0, J).
    
        Returns
        -------
        chosen_ids : list
            List of chosen alternatives by ID (len N).
    
        """
        N = len(positions)
        J = len(ids) // N
    
        ids_by_obs = np.reshape(ids, (N,J))
        return [ids_by_obs[i][positions[i]] for i in range(N)]

    
    def run(self):
        """
        Run the model step: calculate simulated choices and use them to update a column.
        
        Predicted probabilities and simulated choices come from ChoiceModels. For now, 
        the choices are unconstrained (any number of choosers can select the same 
        alternative).
        
        The predicted probabilities and simulated choices are saved to the class object 
        for interactive use (`probabilities` with type pd.DataFrame, and `choices` with 
        type pd.Series) but are not persisted in the dictionary representation of the 
        model step.

        """
        observations = self._get_df(tables=self.out_choosers,
                                    fallback_tables = self.choosers, 
                                    filters=self.out_chooser_filters)
        
        alternatives = self._get_df(tables = self.out_alternatives, 
                                    fallback_tables = self.alternatives,
                                    filters = self.out_alt_filters)
        
        numalts = self._get_alt_sample_size()
        
        mct = MergedChoiceTable(observations = observations,
                                alternatives = alternatives,
                                sample_size = numalts)
        mct_df = mct.to_frame()
        
        # Data columns need to align with the coefficients
        dm = patsy.dmatrix(self.model_expression, data=mct_df, return_type='dataframe')
        
        # Get probabilities and choices
        probs = mnl.mnl_simulate(data = dm, coeff = self.fitted_parameters, 
                                 numalts = numalts, returnprobs=True)

        # TO DO - this ends up recalculating the probabilities because there's not 
        # currently a code path to get both at once - fix this)
        choice_positions = mnl.mnl_simulate(data = dm, coeff = self.fitted_parameters, 
                                            numalts = numalts, returnprobs=False)
        
        ids = mct_df[mct.alternative_id_col].tolist()
        choices = self._get_chosen_ids(ids, choice_positions)
        
        # Save results to the class object (via df to include indexes)
        mct_df['probability'] = np.reshape(probs, (probs.size, 1))
        self.probabilities = mct_df[[mct.observation_id_col, 
                                     mct.alternative_id_col, 'probability']]
        observations['choice'] = choices
        self.choices = observations.choice
        
        # Update Orca
        if self.out_choosers is not None:
            table = orca.get_table(self.out_choosers)
        else:
            table = orca.get_table(self.choosers)
        
        if self.out_column is not None:
            column = self.out_column
        else:
            column = self.choice_column
        
        table.update_col_from_series(column, observations.choice, cast=True)
        
        # Print a message about limited usage
        print("Warning: choices are unconstrained; additional functionality in progress")
    
