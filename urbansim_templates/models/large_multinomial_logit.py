from __future__ import print_function

import orca
from urbansim.models.util import columns_in_formula, apply_filter_query
from choicemodels.tools import MergedChoiceTable
import pandas as pd

from .. import modelmanager
from ..utils import get_data, update_column, to_list, version_greater_or_equal
from .shared import TemplateStep


def check_choicemodels_version():
    try:
        import choicemodels
        assert version_greater_or_equal(choicemodels.__version__, '0.2.dev4')
    except:
        raise ImportError("LargeMultinomialLogitStep requires choicemodels 0.2.dev4 or "
                          "later. For installation instructions, see "
                          "https://github.com/udst/choicemodels.")


@modelmanager.template
class LargeMultinomialLogitStep(TemplateStep):
    """
    Class for building standard multinomial logit model steps where alternatives are 
    interchangeable and all have the same model expression. Supports random sampling of 
    alternatives.

    Estimation and simulation are performed using ChoiceModels.

    Parameters
    ----------
    choosers : str or list of str, optional
        Name(s) of Orca tables to draw choice scenario data from. The first table is the
        primary one. Any additional tables need to have merge relationships ("broadcasts")
        specified so that they can be merged unambiguously onto the first table. The index
        of the primary table should be a unique ID. In this template, the 'choosers' and
        'alternatives' parameters replace the 'tables' parameter. Both are required for 
        fitting a model, but do not have to be provided when the object is created.
        Reserved column names: 'chosen'.

    alternatives : str or list of str, optional
        Name(s) of Orca tables containing data about alternatives. The first table is the
        primary one. Any additional tables need to have merge relationships ("broadcasts")
        specified so that they can be merged unambiguously onto the first table. The index
        of the primary table should be a unique ID. In this template, the 'choosers' and
        'alternatives' parameters replace the 'tables' parameter. Both are required for 
        fitting a model, but do not have to be provided when the object is created.
        Reserved column names: 'chosen'.

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
        `choice_column` will be used. If the column already exists, choices will be cast 
        to match its data type. If the column is generated on the fly, it will be given 
        the same data type as the index of the alternatives table. Replaces the 
        `out_fname` argument in UrbanSim. 

    out_chooser_filters : str or list of str, optional
        Filters to apply to the chooser data before simulation. If not provided, no 
        filters will be applied. Replaces the `predict_filters` argument in UrbanSim.

    out_alt_filters : str or list of str, optional
        Filters to apply to the alternatives data before simulation. If not provided, no 
        filters will be applied. Replaces the `predict_filters` argument in UrbanSim.

    constrained_choices : bool, optional
        "True" means alternatives have limited capacity. "False" (default) means that 
        alternatives can accommodate an unlimited number of choosers. 

    alt_capacity : str, optional
        Name of a column in the out_alternatives table that expresses the capacity of
        alternatives. If not provided and constrained_choices is True, each alternative
        is interpreted as accommodating a single chooser. 

    chooser_size : str, optional
        Name of a column in the out_choosers table that expresses the size of choosers.
        Choosers might have varying sizes if the alternative capacities are amounts 
        rather than counts -- e.g. square footage. Chooser sizes must be in the same units
        as alternative capacities. If not provided and constrained_choices is True, each
        chooser has a size of 1.

    max_iter : int or None, optional
        Maximum number of choice simulation iterations. If None (default), the algorithm
        will iterate until all choosers are matched or no alternatives remain.

    name : str, optional
        Name of the model step, passed to ModelManager. If none is provided, a name is
        generated each time the `fit()` method runs.

    tags : list of str, optional
        Tags, passed to ModelManager.

    Attributes
    ----------
    All parameters can also be get and set as properties. The following attributes should
    be treated as read-only.

    choices : pd.Series
        Available after the model step is run. List of chosen alternative id's, indexed 
        with the chooser id. Does not persist when the model step is reloaded from 
        storage.

    mergedchoicetable : choicemodels.tools.MergedChoiceTable
        Table built for estimation or simulation. Does not persist when the model step is 
        reloaded from storage. Not available if choices have capacity constraints,
        because multiple choice tables are generated iteratively.

    model : choicemodels.MultinomialLogitResults
        Available after a model has been fit. Persists when reloaded from storage.

    probabilities : pd.Series
        Available after the model step is run -- but not if choices have capacity 
        constraints, which requires probabilities to be calculated multiple times. 
        Provides list of probabilities corresponding to the sampled alternatives, indexed 
        with the chooser and alternative id's. Does not persist when the model step is 
        reloaded from storage.

    """

    def __init__(self, choosers=None, alternatives=None, model_expression=None,
                 choice_column=None, chooser_filters=None, chooser_sample_size=None,
                 alt_filters=None, alt_sample_size=None, out_choosers=None,
                 out_alternatives=None, out_column=None, out_chooser_filters=None,
                 out_alt_filters=None, constrained_choices=False, alt_capacity=None,
                 chooser_size=None, max_iter=None, mct_intx_ops=None, name=None, tags=[]):

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
        self.constrained_choices = constrained_choices
        self.alt_capacity = alt_capacity
        self.chooser_size = chooser_size
        self.max_iter = max_iter
        self.mct_intx_ops = mct_intx_ops

        # Placeholders for model fit data, filled in by fit() or from_dict()
        self.summary_table = None
        self.fitted_parameters = None
        self.model = None

        # Placeholders for diagnostic data, filled in by fit() or run()
        self.mergedchoicetable = None
        self.probabilities = None
        self.choices = None



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
        check_choicemodels_version()
        from choicemodels import MultinomialLogitResults

        # Pass values from the dictionary to the __init__() method
        obj = cls(choosers=d['choosers'], alternatives=d['alternatives'],
                  model_expression=d['model_expression'], choice_column=d['choice_column'],
                  chooser_filters=d['chooser_filters'],
                  chooser_sample_size=d['chooser_sample_size'],
                  alt_filters=d['alt_filters'], alt_sample_size=d['alt_sample_size'],
                  out_choosers=d['out_choosers'], out_alternatives=d['out_alternatives'],
                  out_column=d['out_column'], out_chooser_filters=d['out_chooser_filters'],
                  out_alt_filters=d['out_alt_filters'],
                  constrained_choices=d['constrained_choices'], alt_capacity=d['alt_capacity'],
                  chooser_size=d['chooser_size'], max_iter=d['max_iter'],
                  mct_intx_ops=d.get('mct_intx_ops', None), name=d['name'],
                  tags=d['tags'])

        # Load model fit data
        obj.summary_table = d['summary_table']
        obj.fitted_parameters = d['fitted_parameters']

        if obj.fitted_parameters is not None:
            obj.model = MultinomialLogitResults(model_expression=obj.model_expression,
                                                fitted_parameters=obj.fitted_parameters)

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
            'constrained_choices': self.constrained_choices,
            'alt_capacity': self.alt_capacity,
            'chooser_size': self.chooser_size,
            'max_iter': self.max_iter,
            'mct_intx_ops': self.mct_intx_ops,
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

    @property
    def constrained_choices(self):
        return self.__constrained_choices

    @constrained_choices.setter
    def constrained_choices(self, value):
        self.__constrained_choices = value
        self.send_to_listeners('constrained_choices', value)

    @property
    def alt_capacity(self):
        return self.__alt_capacity

    @alt_capacity.setter
    def alt_capacity(self, value):
        self.__alt_capacity = value
        self.send_to_listeners('alt_capacity', value)

    @property
    def chooser_size(self):
        return self.__chooser_size

    @chooser_size.setter
    def chooser_size(self, value):
        self.__chooser_size = value
        self.send_to_listeners('chooser_size', value)

    @property
    def max_iter(self):
        return self.__max_iter

    @max_iter.setter
    def max_iter(self, value):
        self.__max_iter = value
        self.send_to_listeners('max_iter', value)

    @property
    def mct_intx_ops(self):
        return self.__mct_intx_ops

    @mct_intx_ops.setter
    def mct_intx_ops(self, value):
        self.__mct_intx_ops = value
        self.send_to_listeners('mct_intx_ops', value)

    def perform_mct_intx_ops(self, mct, nan_handling='zero'):
        """
        Method to dynamically update a MergedChoiceTable object according to
        a pre-defined set of operations specified in the model .yaml config.
        Operations are performed sequentially as follows: 1) Pandas merges
        with other Orca tables; 2) Pandas group-by aggregations; 3) rename
        existing columns; 4) create new columns via Pandas `eval()`.

        Parameters
        ----------
        mct : choicemodels.tools.MergedChoiceTable
        nan_handling : str
            Either 'zero' or 'drop', where the former will replace all NaN's
            and None's with 0 integers and the latter will drop all rows with
            any NaN or Null values.

        Returns
        -------
        MergedChoiceTable
        """

        intx_ops = self.mct_intx_ops
        mct_df = mct.to_frame()
        og_mct_index = mct_df.index.names
        mct_df.reset_index(inplace=True)
        mct_df.index.name = 'mct_index'

        # merges
        intx_df = mct_df.copy()
        for merge_args in intx_ops.get('successive_merges', []):

            # make sure mct index is preserved during merge
            left_cols = merge_args.get('mct_cols', intx_df.columns)
            left_idx = merge_args.get('left_index', False)

            if intx_df.index.name == mct_df.index.name:
                if not left_idx:
                    intx_df.reset_index(inplace=True)
                    if mct_df.index.name not in left_cols:
                        left_cols += [mct_df.index.name]
            elif mct_df.index.name in intx_df.columns:
                if mct_df.index.name not in left_cols:
                    left_cols += [mct_df.index.name]
            else:
                raise KeyError(
                    'Column {0} must be preserved in intx ops!'.format(
                        mct_df.index.name))

            left = intx_df[left_cols]

            right = get_data(
                merge_args['right_table'],
                extra_columns=merge_args.get('right_cols', None))

            intx_df = pd.merge(
                left, right,
                how=merge_args.get('how', 'inner'),
                on=merge_args.get('on_cols', None),
                left_on=merge_args.get('left_on', None),
                right_on=merge_args.get('right_on', None),
                left_index=left_idx,
                right_index=merge_args.get('right_index', False),
                suffixes=merge_args.get('suffixes', ('_x', '_y')))

        # aggs
        aggs = intx_ops.get('aggregations', False)
        if aggs:
            intx_df = intx_df.groupby('mct_index').agg(aggs)

        # rename cols
        if intx_ops.get('rename_cols', False):
            intx_df = intx_df.rename(
                columns=intx_ops['rename_cols'])

        # update mct
        mct_df = pd.merge(mct_df, intx_df, on='mct_index')

        # create new cols from expressions
        for eval_op in intx_ops.get('sequential_eval_ops', []):
            new_col = eval_op['name']
            expr = eval_op['expr']
            engine = eval_op.get('engine', 'numexpr')
            mct_df[new_col] = mct_df.eval(expr, engine=engine)

        # restore original mct index
        mct_df.set_index(og_mct_index, inplace=True)

        # handle NaNs and Nones
        if mct_df.isna().values.any():
            if nan_handling == 'zero':
                print("Replacing MCT None's and NaN's with 0")
                mct_df = mct_df.fillna(0)
            elif nan_handling == 'drop':
                print("Dropping rows with None's/NaN's from MCT")
                mct_df = mct_df.dropna(axis=0)

        return MergedChoiceTable.from_df(mct_df)

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
            complicated choice table than can be generated within the template, for 
            example including sampling weights or interaction terms. 

        Returns
        -------
        None

        """
        check_choicemodels_version()
        from choicemodels import MultinomialLogit
        from choicemodels.tools import MergedChoiceTable

        if (mct is not None):
            df_from_mct = mct.to_frame()
            idx_names = df_from_mct.index.names
            df_from_mct = df_from_mct.reset_index()
            df_from_mct = apply_filter_query(
                df_from_mct, self.chooser_filters).set_index(idx_names)
            mct = MergedChoiceTable.from_df(df_from_mct)

        else:
            observations = get_data(tables=self.choosers,
                                    filters=self.chooser_filters,
                                    model_expression=self.model_expression,
                                    extra_columns=self.choice_column)

            if (self.chooser_sample_size is not None):
                observations = observations.sample(self.chooser_sample_size)

            alternatives = get_data(tables=self.alternatives,
                                    filters=self.alt_filters,
                                    model_expression=self.model_expression)

            mct = MergedChoiceTable(observations=observations,
                                    alternatives=alternatives,
                                    chosen_alternatives=self.choice_column,
                                    sample_size=self.alt_sample_size)

        model = MultinomialLogit(data=mct,
                                 model_expression=self.model_expression)
        results = model.fit()

        self.name = self._generate_name()
        self.summary_table = str(results)
        print(self.summary_table)

        coefs = results.get_raw_results()['fit_parameters']['Coefficient']
        self.fitted_parameters = coefs.tolist()
        self.model = results

        # Save merged choice table to the class object for diagnostics
        self.mergedchoicetable = mct

    def run(self, chooser_batch_size=None, interaction_terms=None):
        """
        Run the model step: simulate choices and use them to update an Orca column.

        The simulated choices are saved to the class object for diagnostics. If choices 
        are unconstrained, the choice table and the probabilities of sampled alternatives 
        are saved as well.

        Parameters
        ----------
        chooser_batch_size : int
            This parameter gets passed to 
            choicemodels.tools.simulation.iterative_lottery_choices and is a temporary
            workaround for dealing with memory issues that arise from generating massive
            merged choice tables for simulations that involve large numbers of choosers,
            large numbers of alternatives, and large numbers of predictors. It allows the
            user to specify a batch size for simulating choices one chunk at a time. 

        interaction_terms : pandas.Series, pandas.DataFrame, or list of either, optional
            Additional column(s) of interaction terms whose values depend on the 
            combination of observation and alternative, to be merged onto the final data 
            table. If passed as a Series or DataFrame, it should include a two-level 
            MultiIndex. One level's name and values should match an index or column from 
            the observations table, and the other should match an index or column from the 
            alternatives table. 

        Returns
        -------
        None

        """
        check_choicemodels_version()
        from choicemodels import MultinomialLogit
        from choicemodels.tools import (MergedChoiceTable, monte_carlo_choices,
                                        iterative_lottery_choices)

        # Clear simulation attributes from the class object
        self.mergedchoicetable = None
        self.probabilities = None
        self.choices = None

        if interaction_terms is not None:
            uniq_intx_idx_names = set([
                idx for intx in interaction_terms for idx in intx.index.names])
            obs_extra_cols = to_list(self.chooser_size) + \
                list(uniq_intx_idx_names)
            alts_extra_cols = to_list(
                self.alt_capacity) + list(uniq_intx_idx_names)

        else:
            obs_extra_cols = to_list(self.chooser_size)
            alts_extra_cols = to_list(self.alt_capacity)

        # get any necessary extra columns from the mct intx operations spec
        if self.mct_intx_ops:
            intx_extra_obs_cols = self.mct_intx_ops.get('extra_obs_cols', [])
            intx_extra_obs_cols = to_list(intx_extra_obs_cols)
            obs_extra_cols += intx_extra_obs_cols
            intx_extra_alts_cols = self.mct_intx_ops.get('extra_alts_cols', [])
            intx_extra_alts_cols = to_list(intx_extra_alts_cols)
            alts_extra_cols += intx_extra_alts_cols

        observations = get_data(tables=self.out_choosers,
                                fallback_tables=self.choosers,
                                filters=self.out_chooser_filters,
                                model_expression=self.model_expression,
                                extra_columns=obs_extra_cols)

        if len(observations) == 0:
            print("No valid choosers")
            return

        alternatives = get_data(tables=self.out_alternatives,
                                fallback_tables=self.alternatives,
                                filters=self.out_alt_filters,
                                model_expression=self.model_expression,
                                extra_columns=alts_extra_cols)

        if len(alternatives) == 0:
            print("No valid alternatives")
            return

        # Remove filter columns before merging, in case column names overlap
        expr_cols = columns_in_formula(self.model_expression)

        obs_cols = set(observations.columns) & set(
            expr_cols + to_list(obs_extra_cols))
        observations = observations[list(obs_cols)]

        alt_cols = set(alternatives.columns) & set(
            expr_cols + to_list(alts_extra_cols))
        alternatives = alternatives[list(alt_cols)]

        # Callables for iterative choices
        def mct(obs, alts, intx_ops=None):

            this_mct = MergedChoiceTable(
                obs, alts, sample_size=self.alt_sample_size,
                interaction_terms=interaction_terms)

            if intx_ops:
                this_mct = self.perform_mct_intx_ops(this_mct)
                this_mct.sample_size = self.alt_sample_size

            return this_mct

        def probs(mct):
            return self.model.probabilities(mct)

        if self.constrained_choices is True:
            choices = iterative_lottery_choices(
                observations, alternatives,
                mct_callable=mct,
                probs_callable=probs,
                alt_capacity=self.alt_capacity, chooser_size=self.chooser_size,
                max_iter=self.max_iter, chooser_batch_size=chooser_batch_size,
                mct_intx_ops=self.mct_intx_ops)

        else:
            choicetable = mct(
                observations, alternatives, intx_ops=self.mct_intx_ops)
            probabilities = probs(choicetable)
            choices = monte_carlo_choices(probabilities)

            # Save data to class object if available
            self.mergedchoicetable = choicetable
            self.probabilities = probabilities

        # Save choices to class object for diagnostics
        self.choices = choices

        # Update Orca
        update_column(table=self.out_choosers,
                      fallback_table=self.choosers,
                      column=self.out_column,
                      fallback_column=self.choice_column,
                      data=choices)
