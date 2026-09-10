import orca
import numpy as np
import pandas as pd
import pytest

from choicemodels import MultinomialLogitResults

from urbansim_templates import modelmanager
from urbansim_templates.models import LargeMultinomialLogitStep
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    d1 = {'oid': np.arange(10), 
          'obsval': np.random.random(10),
          'choice': np.random.choice(np.arange(20), size=10)}

    d2 = {'aid': np.arange(20), 
          'altval': np.random.random(20)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


def test_template_validity():
    """
    Run the template through the standard validation check.
    
    """
    assert validate_template(LargeMultinomialLogitStep)


def test_observation_sampling(orca_session):
    modelmanager.initialize()

    m = LargeMultinomialLogitStep()
    m.choosers = 'obs'
    m.alternatives = 'alts'
    m.choice_column = 'choice'
    m.model_expression = 'obsval + altval'
    
    m.fit()
    assert(len(m.mergedchoicetable.to_frame()) == 200)
    
    m.chooser_sample_size = 5
    m.fit()
    assert(len(m.mergedchoicetable.to_frame()) == 100)
    
    m.name = 'mnl-test'
    modelmanager.register(m)
    
    modelmanager.initialize()
    m = modelmanager.get_step('mnl-test')
    assert(m.chooser_sample_size == 5)
    
    modelmanager.remove_step('mnl-test')


@pytest.fixture
def data():
    num_obs = 100
    num_alts = 120
    
    d1 = {'oid': np.arange(num_obs), 
          'obsval': np.random.random(num_obs),
          'choice': np.random.choice(np.arange(num_alts), size=num_obs)}

    d2 = {'aid': np.arange(num_alts), 
          'altval': np.random.random(num_alts)}

    obs = pd.DataFrame(d1).set_index('oid')
    orca.add_table('obs', obs)

    alts = pd.DataFrame(d2).set_index('aid')
    orca.add_table('alts', alts)


@pytest.fixture
def m(data):
    """
    Build a fitted model.
    
    """
    m = LargeMultinomialLogitStep()
    m.choosers = 'obs'
    m.alternatives = 'alts'
    m.choice_column = 'choice'
    m.model_expression = 'obsval + altval'
    m.alt_sample_size = 10
    
    m.fit()
    return m


def test_property_persistence(m):
    """
    Test persistence of properties across registration, saving, and reloading.
    
    """
    m.fit()
    m.name = 'my-model'
    m.tags = ['tag1']
    m.chooser_filters = 'filters1'
    m.chooser_sample_size = 100
    m.alt_filters = 'filter2'
    m.out_choosers = 'choosers2'
    m.out_alternatives = 'alts2'
    m.out_column = 'choices'
    m.out_chooser_filters = 'filters3'
    m.out_alt_filters = 'filters4'
    m.constrained_choices = True
    m.alt_capacity = 'cap'
    m.chooser_size = 'size'
    m.max_iter = 17
    
    d1 = m.to_dict()
    modelmanager.initialize()
    modelmanager.register(m)
    modelmanager.initialize()
    d2 = modelmanager.get_step('my-model').to_dict()
    
    assert d1 == d2
    modelmanager.remove_step('my-model')
    

def test_simulation_unconstrained(m):
    """
    Test simulation chooser filters with unconstrained choices.
    
    """
    obs = orca.get_table('obs').to_frame()
    obs.loc[:24, 'choice'] = -1
    orca.add_table('obs', obs)
    
    m.out_chooser_filters = 'choice == -1'
    m.run()
    
    assert len(m.choices) == 25
    
    obs = orca.get_table('obs').to_frame()
    assert sum(obs.choice == -1) == 0
    assert obs.loc[:24, 'choice'].equals(m.choices)
    
    
def test_simulation_single_occupancy(m):
    """
    Test simulation of single-occupancy choices.
    
    """
    m.constrained_choices = True
    m.run()
    
    obs = orca.get_table('obs').to_frame()
    assert len(obs) == len(obs.choice.unique())
    
    
def test_simulation_constrained(m):
    """
    Test simulation of choices with explicit capacities and sizes.
    
    """
    obs = orca.get_table('obs').to_frame()
    obs.loc[:,'choice'] = -1
    obs['size'] = np.random.choice([1,2], size=len(obs))
    orca.add_table('obs', obs)
    
    alts = orca.get_table('alts').to_frame()
    alts['cap'] = np.random.choice([1,2,3], size=len(alts))
    orca.add_table('alts', alts)
    
    m.constrained_choices = True
    m.alt_capacity = 'cap'
    m.chooser_size = 'size'
    m.run()
    
    obs = orca.get_table('obs').to_frame()
    assert all(~obs.choice.isin([-1]))


@pytest.fixture
def zones(data):
    """
    Add a 'zones' table and a zone id column on the alternatives, for testing merge 
    operations on the choice table.
    
    """
    alts = orca.get_table('alts').to_frame()
    alts['zone_id'] = np.random.choice(np.arange(5), size=len(alts))
    orca.add_table('alts', alts)
    
    zones = pd.DataFrame({'zone_id': np.arange(5),
                          'zone_val': np.random.random(5),
                          'coord_y': np.random.random(5)}).set_index('zone_id')
    orca.add_table('zones', zones)


def test_mct_intx_ops_merge(m, zones):
    """
    Test post-merge operations on the choice table: a merge that carries every choice 
    table column along (no `mct_cols`), followed by an eval expression (#126, #130). 
    
    Columns that come back from the operations but already exist in the choice table are 
    dropped in favor of the originals, without touching other columns -- including ones 
    whose names happen to end in a merge suffix like '_y'.
    
    """
    from choicemodels.tools import MergedChoiceTable
    
    obs = orca.get_table('obs').to_frame()
    alts = orca.get_table('alts').to_frame()
    mct = MergedChoiceTable(obs, alts, sample_size=10)
    
    m.mct_intx_ops = {
        'successive_merges': [{
            'right_table': 'zones',
            'right_cols': ['zone_val', 'coord_y'],
            'left_on': 'zone_id',
            'right_index': True}],
        'sequential_eval_ops': [{
            'name': 'zone_val_x2', 'expr': 'zone_val * 2', 'engine': 'python'}]}
    
    df_in = mct.to_frame().copy()
    df_out = m.perform_mct_intx_ops(mct).to_frame()
    
    assert mct.to_frame().equals(df_in)  # input table is not modified
    assert len(df_out) == len(df_in)
    assert df_out.index.names == df_in.index.names
    assert set(df_out.columns) == set(df_in.columns) | {'zone_val', 'coord_y', 
                                                        'zone_val_x2'}
    assert (df_out.zone_val_x2 == df_out.zone_val * 2).all()


def test_mct_intx_ops_aggregation(m, zones):
    """
    Test post-merge operations that specify `mct_cols` and aggregate the merged data 
    back to one row per choice table entry, then rename the result.
    
    """
    from choicemodels.tools import MergedChoiceTable
    
    obs = orca.get_table('obs').to_frame()
    alts = orca.get_table('alts').to_frame()
    mct = MergedChoiceTable(obs, alts, sample_size=10)
    
    m.mct_intx_ops = {
        'successive_merges': [{
            'right_table': 'zones',
            'right_cols': ['zone_val'],
            'mct_cols': ['zone_id'],
            'left_on': 'zone_id',
            'right_index': True}],
        'aggregations': {'zone_val': 'max'},
        'rename_cols': {'zone_val': 'zone_val_max'}}
    
    df_in = mct.to_frame().copy()
    df_out = m.perform_mct_intx_ops(mct).to_frame()
    
    assert mct.to_frame().equals(df_in)  # input table is not modified
    assert len(df_out) == len(df_in)
    assert df_out.index.names == df_in.index.names
    assert set(df_out.columns) == set(df_in.columns) | {'zone_val_max'}


def test_simulation_no_valid_choosers(m):
    """
    If there are no valid choosers after applying filters, simulation should exit.
    
    """
    m.out_chooser_filters = 'choice == -1'
    m.run()
    

def test_simulation_no_valid_alternatives(m):
    """
    If there are no valid alternatives after applying filters, simulation should exit.
    
    """
    m.out_alt_filters = 'altval == -1'
    m.run()
    

def test_output_column_autocreation(m):
    """
    Test on-the-fly creation of the output column.
    
    """
    m.out_column = 'potato_chips'
    m.run()
    
    assert('potato_chips' in orca.get_table('obs').columns)
    assert(m.choices.equals(orca.get_table('obs').to_frame()['potato_chips']))
    

def test_diagnostic_attributes(data):
    """
    Test that diagnostic attributes are available when expected.
    
    """
    m = LargeMultinomialLogitStep()
    m.choosers = 'obs'
    m.alternatives = 'alts'
    m.choice_column = 'choice'
    m.model_expression = 'obsval + altval'
    m.alt_sample_size = 10
    
    assert(m.model is None)
    assert(m.mergedchoicetable is None)
    assert(m.probabilities is None)
    assert(m.choices is None)
    
    m.fit()
    
    assert(isinstance(m.model, MultinomialLogitResults))
    
    len_mct = len(m.mergedchoicetable.to_frame())
    len_obs_alts = len(orca.get_table(m.choosers).to_frame()) * m.alt_sample_size
    
    assert(len_mct == len_obs_alts)
    
    name = m.name
    modelmanager.register(m)
    modelmanager.initialize()
    m = modelmanager.get_step(name)
    
    assert(isinstance(m.model, MultinomialLogitResults))

    m.run()

    len_mct = len(m.mergedchoicetable.to_frame())
    len_probs = len(m.probabilities)
    len_choices = len(m.choices)
    len_obs = len(orca.get_table(m.choosers).to_frame())
    len_obs_alts = len_obs * m.alt_sample_size
    
    assert(len_mct == len_obs_alts)
    assert(len_probs == len_obs_alts)
    assert(len_choices == len_obs)

    modelmanager.remove_step(name)


def test_simulation_join_key_as_filter(m):
    """
    This tests that it's possible to use a join key as a both a data filter for one of 
    the tables, and as a choice column for the model. 
    
    This came up because MergedChoiceTable doesn't allow the observations and 
    alternatives to have any column names in common -- the rationale is to maintain data 
    traceability by avoiding any of-the-fly renaming or dropped columns. 
    
    In the templates, in order to support things like using 'households.building_id' as a 
    filter column and 'buildings.building_id' as a choice column, we apply the filters 
    and then drop columns that are no longer needed before merging the tables. 
    
    """
    obs = orca.get_table('obs')
    obs['aid'] = obs.get_column('choice')
    
    m.out_choosers = 'obs'
    m.out_chooser_filters = 'aid > 50'
    m.out_alternatives = 'alts'
    m.out_column = 'aid'
    
    m.run()

