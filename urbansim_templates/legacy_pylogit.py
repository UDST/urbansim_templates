"""Conversion of trusted historical PyLogit model pickles."""

from __future__ import print_function

import os
import pickle

import pandas as pd
from urbansim.utils import yamlio


class LegacyPyLogitObject(object):
    """Inert carrier for state formerly attached to a PyLogit class."""


def _unavailable_pylogit_function(*args, **kwargs):
    raise RuntimeError("PyLogit functions are unavailable during conversion")


_ALLOWED_GLOBALS = {
    ('builtins', 'slice'),
    ('__builtin__', 'slice'),
    ('collections', 'OrderedDict'),
    ('numpy', 'ndarray'),
    ('numpy', 'dtype'),
    ('numpy.core.multiarray', '_reconstruct'),
    ('numpy.core.multiarray', 'scalar'),
    ('numpy.core.numeric', '_frombuffer'),
    ('numpy._core.multiarray', '_reconstruct'),
    ('numpy._core.multiarray', 'scalar'),
    ('numpy._core.numeric', '_frombuffer'),
    ('pandas', 'DataFrame'),
    ('pandas', 'Index'),
    ('pandas', 'RangeIndex'),
    ('pandas', 'Series'),
    ('pandas', 'StringDtype'),
    ('pandas.core.frame', 'DataFrame'),
    ('pandas.core.indexes.base', 'Index'),
    ('pandas._libs.arrays', '__pyx_unpickle_NDArrayBacked'),
    ('pandas._libs.internals', '_unpickle_block'),
    ('pandas.arrays', 'StringArray'),
    ('pandas.core.indexes.base', '_new_Index'),
    ('pandas.core.indexes.range', 'RangeIndex'),
    ('pandas.core.internals.managers', 'BlockManager'),
    ('pandas.core.internals.managers', 'SingleBlockManager'),
    ('pandas.core.series', 'Series'),
}


class RestrictedPyLogitUnpickler(pickle.Unpickler):
    """Load PyLogit state without importing or executing PyLogit code."""

    def find_class(self, module, name):
        if module.startswith('pylogit.'):
            if name == 'MNL':
                return LegacyPyLogitObject
            return _unavailable_pylogit_function
        if (module == 'pandas.core.indexes.numeric' and
                name in ('Int64Index', 'UInt64Index', 'Float64Index')):
            return pd.Index
        if (module, name) not in _ALLOWED_GLOBALS:
            raise pickle.UnpicklingError(
                "Unsupported object in legacy model: {}.{}".format(module, name))
        return super(RestrictedPyLogitUnpickler, self).find_class(module, name)


def load_legacy_pylogit_model(path):
    """Load a trusted PyLogit model into an inert state carrier."""
    with open(path, 'rb') as stream:
        model = RestrictedPyLogitUnpickler(stream).load()
    if not isinstance(model, LegacyPyLogitObject):
        raise ValueError("The pickle does not contain a PyLogit MNL model")
    if not hasattr(model, 'params'):
        raise ValueError("The PyLogit model does not contain fitted parameters")
    return model


def convert_legacy_pylogit_config(config_path, pickle_path=None,
                                    output_dir=None):
    """Write a parameter-based copy of a saved small-MNL configuration.

    The input files are never modified. Pickle files must be trusted even
    though loading is restricted to the known scientific-Python object types.
    """
    config_path = os.path.abspath(config_path)
    document = yamlio.yaml_to_dict(str_or_buffer=config_path)
    saved_object = document.get('saved_object')
    if saved_object is None:
        raise ValueError("Configuration has no saved_object")
    template = saved_object.get('template')
    if template != 'SmallMultinomialLogitStep':
        raise ValueError(
            "Configuration is not a SmallMultinomialLogitStep: {}".format(template))

    name = saved_object.get('name')
    if not name:
        raise ValueError("Saved model has no name")
    if pickle_path is None:
        pickle_path = os.path.join(
            os.path.dirname(config_path), name + '-model-object.pkl')
    model = load_legacy_pylogit_model(pickle_path)

    params = model.params
    parameter_values = params.tolist() if hasattr(params, 'tolist') else list(params)
    parameter_names = (params.index.tolist()
                       if hasattr(params, 'index') else None)
    saved_object['model_storage_version'] = 1
    saved_object['fitted_parameters'] = parameter_values
    if parameter_names is not None:
        saved_object['fitted_parameter_names'] = parameter_names

    supplemental = [item for item in saved_object.get('supplemental_objects', [])
                    if item and item.get('name') != 'model-object']
    if supplemental:
        saved_object['supplemental_objects'] = supplemental
    else:
        saved_object.pop('supplemental_objects', None)

    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(config_path), 'converted')
    output_dir = os.path.abspath(output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_path = os.path.join(output_dir, os.path.basename(config_path))
    if os.path.exists(output_path):
        raise IOError("Output already exists: {}".format(output_path))

    yamlio.convert_to_yaml(document, output_path)
    return output_path
