Migrating saved PyLogit models
==============================

Earlier versions of ``SmallMultinomialLogitStep`` stored the complete PyLogit
estimator in a pickle file. Current versions store the model specification,
labels, and fitted coefficients in YAML. The parameter-based representation is
portable across compatible ChoiceModels releases and does not require PyLogit
for routine use.

Convert each existing model without installing PyLogit::

    from urbansim_templates.legacy_pylogit import convert_legacy_pylogit_config

    converted = convert_legacy_pylogit_config(
        "configs/my-model.yaml",
        "configs/my-model-model-object.pkl",
        output_dir="converted-configs")
    print(converted)

The converter maps the historical PyLogit class to an inert state carrier and
allows only the NumPy and pandas object types used by the saved model. It
extracts the fitted coefficients and writes ``converted-configs/my-model.yaml``.
The input YAML and pickle are not modified. Initialize ModelManager from the
converted directory, which must not also contain the original pickle-based
YAML files::

    modelmanager.initialize("converted-configs")

Pickle is not a safe interchange format. Convert only files from a trusted
source. Review the converted coefficients and exercise the model in simulation
before replacing the original configuration. An unexpected object type causes
the conversion to stop rather than broadening what the unpickler accepts.
