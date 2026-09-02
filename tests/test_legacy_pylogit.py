from collections import OrderedDict
from pathlib import Path
import pickle
import sys
import types

import numpy as np
import orca
import pandas as pd
import pytest
from urbansim.utils import yamlio

from urbansim_templates.legacy_pylogit import (
    convert_legacy_pylogit_config,
    load_legacy_pylogit_model,
)
from urbansim_templates import modelmanager
from urbansim_templates.models import SmallMultinomialLogitStep  # noqa: F401


FIXTURES = Path(__file__).parent / 'fixtures' / 'legacy_pylogit'


def _write_legacy_model(path):
    package = types.ModuleType('pylogit')
    module = types.ModuleType('pylogit.conditional_logit')
    model_type = type('MNL', (object,), {})
    model_type.__module__ = module.__name__
    module.MNL = model_type
    package.conditional_logit = module
    sys.modules['pylogit'] = package
    sys.modules[module.__name__] = module
    try:
        model = model_type()
        model.params = pd.Series(
            [0.25, -0.5, 1.75], index=['ASC 1', 'ASC 2', 'income'])
        with path.open('wb') as stream:
            pickle.dump(model, stream, protocol=pickle.HIGHEST_PROTOCOL)
    finally:
        del sys.modules[module.__name__]
        del sys.modules['pylogit']


def test_load_without_pylogit(tmp_path):
    model_path = tmp_path / 'small-model-model-object.pkl'
    _write_legacy_model(model_path)

    model = load_legacy_pylogit_model(str(model_path))

    assert model.params.tolist() == [0.25, -0.5, 1.75]
    assert model.params.index.tolist() == ['ASC 1', 'ASC 2', 'income']


def test_convert_writes_new_yaml_and_preserves_inputs(tmp_path):
    model_path = tmp_path / 'small-model-model-object.pkl'
    config_path = tmp_path / 'small-model.yaml'
    _write_legacy_model(model_path)
    document = OrderedDict([
        ('modelmanager_version', '0.2.dev9'),
        ('saved_object', OrderedDict([
            ('template', 'SmallMultinomialLogitStep'),
            ('name', 'small-model'),
            ('model_expression_keys', ['intercept', 'income']),
            ('model_expression_values', [[1, 2], [[0, 1, 2]]]),
            ('supplemental_objects', [OrderedDict([
                ('name', 'model-object'),
                ('content_type', 'pickle'),
                ('required', True),
            ])]),
        ])),
    ])
    yamlio.convert_to_yaml(document, str(config_path))
    original_yaml = config_path.read_bytes()
    original_pickle = model_path.read_bytes()

    output = convert_legacy_pylogit_config(str(config_path))
    converted = yamlio.yaml_to_dict(str_or_buffer=output)
    saved = converted['saved_object']

    assert output.endswith('converted/small-model.yaml')
    assert saved['model_storage_version'] == 1
    assert saved['fitted_parameters'] == [0.25, -0.5, 1.75]
    assert saved['fitted_parameter_names'] == ['ASC 1', 'ASC 2', 'income']
    assert 'supplemental_objects' not in saved
    assert config_path.read_bytes() == original_yaml
    assert model_path.read_bytes() == original_pickle

    with pytest.raises(IOError, match='Output already exists'):
        convert_legacy_pylogit_config(str(config_path))


def test_rejects_unexpected_pickle_globals(tmp_path):
    model_path = tmp_path / 'unexpected.pkl'
    with model_path.open('wb') as stream:
        pickle.dump(eval, stream, protocol=pickle.HIGHEST_PROTOCOL)

    with pytest.raises(pickle.UnpicklingError, match='Unsupported object'):
        load_legacy_pylogit_model(str(model_path))


def test_convert_genuine_pylogit_model_and_run(tmp_path):
    config_path = FIXTURES / 'tenure-small-mnl.yaml'
    pickle_path = FIXTURES / 'tenure-small-mnl-model-object.pkl'
    output_dir = tmp_path / 'converted'

    converted_path = convert_legacy_pylogit_config(
        str(config_path), str(pickle_path), str(output_dir))
    assert Path(converted_path) == output_dir / 'tenure-small-mnl.yaml'
    assert config_path.exists()
    assert pickle_path.exists()

    households = pd.DataFrame({
        'income': np.linspace(20, 120, 20),
        'hhsize': np.tile([1, 2, 3, 4], 5),
        'tenure': np.tile([0, 1, 2, 0], 5),
    })
    orca.add_table('households', households)
    modelmanager.initialize(str(output_dir))
    step = modelmanager.get_step('tenure-small-mnl')

    np.testing.assert_allclose(step.model.fitted_parameters, [
        2.7064844067439028e-05,
        -0.00025711601864067076,
        0.0029142070849614995,
        -0.0006427900466016769,
    ])
    assert step.fitted_parameter_names == [
        'ASC 1', 'ASC 2', 'inc x 1', 'hh x 2']

    step.out_column = 'simulated_tenure'
    step.run()
    assert step.choices.size == households.shape[0]
