# UrbanSim Templates change log

## 0.3rc1 (2026-09-16)

The first production release of UrbanSim Templates since 0.1.4 in February 2021. It
modernizes the package for current Python and dependency versions, replaces the pickled
PyLogit estimators in saved small-MNL models with portable parameter storage, and
incorporates fixes contributed since 2020. It also includes the changes from the 0.2
development releases of 2019 and 2020, listed below, which were never published as a
production release.

- supports Python 3.10 through 3.14, tested at the oldest and newest, with NumPy 1.26
  through 2.x, Pandas 2.2 through 3.x, Patsy 0.5.6+, SciPy 1.10+, Statsmodels 0.14+,
  Orca 1.8+, UrbanSim 3.3+, and ChoiceModels 0.3+; drops support for Python 3.9 and
  earlier (#134, #136)
- `SmallMultinomialLogitStep` now saves the fitted coefficients and their names in the
  YAML configuration file, instead of pickling the complete estimator object; saved
  models are restored as ChoiceModels results objects and no longer depend on the
  package layout or the NumPy and Pandas versions used when they were fitted (#131)
- **small-MNL configurations saved by earlier versions must be converted before they
  can be loaded**: they stored a pickled PyLogit estimator, which can no longer be
  unpickled because PyLogit is not installed. `modelmanager.initialize()` now raises an
  error pointing to `legacy_pylogit.convert_legacy_pylogit_config()`, which migrates a
  saved configuration without installing PyLogit, writes new files, and leaves the
  originals unchanged (see "Migrating saved PyLogit models" in the documentation) (#131)
- adds an `mct_intx_ops` setting to `LargeMultinomialLogitStep` for interaction-term
  operations (merges, aggregations, renames, and `eval()` expressions) performed on the
  merged choice table after alternatives are sampled during simulation (#126, merged in
  2021 without a release); fixes these operations when `mct_cols` is omitted and when
  user columns end in `_y` (#130)
- fixes interaction terms passed to `LargeMultinomialLogitStep.run()` as a single table
  (#109)
- fixes `fit()` failing in the large MNL templates when a filter column is shared by the
  choosers and alternatives tables (#128)
- fixes `modelmanager.register()` replacing an automatically generated step name (for
  example `LoadTable-20260914-221006`) with a new timestamp, which could leave steps
  reloaded from disk with names that no longer matched their YAML files (#135)
- fixes `utils.parse_version()` and `utils.version_greater_or_equal()` failing on version
  strings with pre-release markers other than `dev`, such as `0.3rc1`, which made
  ModelManager unable to load any saved step under a release-candidate version of the
  package; both now follow the Python packaging standard for version strings, using the
  `packaging` library (#139, closes #57)
- replaces a private Pandas function used to build long-format small-MNL tables, which
  was removed in Pandas 3, and fixes an invalid escape sequence in
  `utils.cols_in_expression()` that raised a SyntaxWarning on Python 3.12 and later (#134)
- declares SciPy and `packaging` as dependencies; `BinaryLogitStep` imports SciPy
  directly, and the version helpers use `packaging`, but both were previously installed
  only as dependencies of Statsmodels and UrbanSim (#136, #139)
- moves package metadata to `pyproject.toml` and removes `setup.py`; ships the tests in
  the source distribution (#134)
- replaces the Travis CI configuration with GitHub Actions continuous integration that
  tests the minimum and current dependency versions on Linux, macOS, and Windows, checks
  code quality, validates the built distributions, and builds the documentation (#134);
  releases are built, verified, and published to PyPI by a GitHub Actions workflow (#137)
- documents the project's scope and status in the README (#133)
- `main` is now the integration branch; `dev` is retired (#137)
- thanks to Paul Waddell for the packaging, CI, and small-MNL storage work; to Max
  Gardner for the interaction-term operations (#126) and the interaction-terms fix
  (#109); to Juan Caicedo for the `mct_intx_ops` fixes (#130); and to Sol Tadeo for the
  filter-column fix (#128)


## 0.2 (development releases only)

#### 0.2.dev9 (2020-05-15)

- fixes a bug in `BinaryLogitStep` simulation where the output is not updated correctly
- adds a `residuals` attribute to fitted `OLSRegressionStep` models, for diagnostics

#### 0.2.dev8 (2020-04-17)

- allows segmented large MNL models to be estimated with a `MergedChoiceTable` that's passed in by the user (rather than generated automatically), thus achieving parity with the non-segmented model class

#### 0.2.dev7 (2019-07-15)

- fixes a bug with the `out_transform` parameter for `OLSRegressionStep`

#### 0.2.dev6 (2019-04-04)

- introduces classes for storing common settings: `shared.CoreTemplateSettings`, `shared.OutputColumnSettings`
- adds new shared functions: `shared.register_column()`, `utils.cols_in_expression()`
- modifies `ColumnFromExpression` template to divide its parameters into three groups

#### 0.2.dev5 (2019-03-29)

- adds new template: `data.ColumnFromExpression`

#### 0.2.dev4 (2019-03-26)

- adds new data management utilities: `utils.validate_table()`, `utils.validate_all_tables()`, `utils.merge_tables()`
- updates `utils.get_data()` to use the new merge tool
- updates `BinaryLogitStep` and `OLSRegressionStep` to use the shared to use `utils.get_data()`, removing any reliance on Orca broadcasts
- raises the `pandas` requirement to 0.23

#### 0.2.dev3 (2019-03-21)

- adds an `mct` argment to `SegmentedLargeMultinomialLogitStep.fit_all()`
- adds an `interaction_terms` argument to `SegmentedLargeMultinomialLogitStep.run_all()`

#### 0.2.dev2 (2019-03-04)

- adds template for saving data: `data.SaveTable()`
- renames `io.TableFromDisk()` to `data.LoadTable()`

#### 0.2.dev1 (2019-02-27)

- fixes a crash in small MNL simulation

#### 0.2.dev0 (2019-02-19)

- adds first data i/o template: `io.TableFromDisk()`
- adds support for `autorun` template property


## 0.1.4 (2021-02-16)

- patch to add a `residuals` attribute to fitted `OLSRegressionStep` models, from 0.2.dev9


## 0.1.3 (2019-07-15)

- patch to incorporate the `out_transform` bug fix for `OLSRegressionStep`, from 0.2.dev7


## 0.1.2 (2019-02-28)

- patch to incorporate the small MNL bug fix from 0.2.dev1


## 0.1.1 (2019-02-05)

#### 0.1.1.dev1 (2019-01-30)

- adds support for passing multiple tables of interaction terms in large MNL
- enables on-the-fly creation of output columns in small MNL

#### 0.1.1.dev0 (2019-01-20)

- allows join keys to be used as data filters in MNL simulation


## 0.1 (2019-01-16)

#### 0.1.dev25 (2019-01-15)

- fixes an OLS simulation bug that raised an error when the output column didn't exist yet
- implements `out_transform` for OLS simulation

#### 0.1.dev24 (2018-12-20)

- fixes a string comparison bug that caused problems with binary logit output in Windows
- adds `model` as an attribute of large MNL model steps, which provides a `choicemodels.MultinomialLogitResults` object and is available any time after a model step is fitted
- enables on-the-fly creation of output columns in large MNL
- fixes a large MNL simulation bug when there are no valid choosers or alternatives after evaluating the filters
- moves unit tests out of the module directory

#### 0.1.dev23 (2018-12-13)

- fixes a bug with interaction terms passed into `LargeMultinomialLogitStep.run()`

#### 0.1.dev22 (2018-12-13)

- narrows the output of `utils.get_data()` to include only the columns requested (plus the index of the primary table) -- previously Orca had also provided some extra columns such as join keys

#### 0.1.dev21 (2018-12-11)

- adds a new function `utils.get_data()` to assemble data from Orca, automatically detecting columns included in model expressions and filters

- implements `SegmentedLargeMultinomialLogit.run_all()`

#### 0.1.dev20 (2018-12-11)

- fixes a model expression persistence bug in the small MNL template

#### 0.1.dev19 (2018-12-06)

- fixes a bug to allow large MNL simulation with multiple chooser tables

#### 0.1.dev18 (2018-11-19)

- improves installation and testing

#### 0.1.dev17 (2018-11-15)

- adds an `interaction_terms` parameter that users can manually pass to `LargeMultinomialLogitStep.run()`, as a temporary solution until interaction terms are fully handled by the templates
- also adds a `chooser_batch_size` parameter in the same place, to reduce memory pressure when there are large numbers of choosers

#### 0.1.dev16 (2018-11-06)

- adds a tool for testing template validity

#### 0.1.dev15 (2018-10-15)

- adds new `LargeMultinomialLogitStep` parameters related to choice simulation: `constrained_choices`, `alt_capacity`, `chooser_size`, and `max_iter`
- updates `LargeMultinomialLogitStep.run()` to use improved simulation utilities from ChoiceModels 0.2.dev4

#### 0.1.dev14 (2018-09-25)

- adds a template for segmented large MNL models: `SegmentedLargeMultinomialLogitStep`, which can automatically generate a set of large MNL models based on segmentation rules

#### 0.1.dev13 (2018-09-24)

- adds a `@modelmanager.template` decorator that makes a class available to the currently running instance of ModelManager

#### 0.1.dev12 (2018-09-19)

- moves the `register()` operation to `modelmanager` (previously it was a method implemented by the individual templates)
- adds general ModelManager support for supplemental objects like pickled model results
