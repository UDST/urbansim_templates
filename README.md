[![Build Status](https://travis-ci.org/UDST/urbansim_templates.svg?branch=master)](https://travis-ci.org/UDST/urbansim_templates)
[![Coverage Status](https://coveralls.io/repos/github/UDST/urbansim_templates/badge.svg?branch=master)](https://coveralls.io/github/UDST/urbansim_templates?branch=master)

# UrbanSim Templates

UrbanSim Templates is a Python library that provides building blocks for Orca-based simulation models. It's part of the [Urban Data Science Toolkit](https://docs.udst.org) (UDST).

The library contains templates for common types of model steps, plus a tool called ModelManager that runs as an extension to the [Orca](https://udst.github.io/orca) task orchestrator. ModelManager can register template-based model steps with the orchestrator, save them to disk, and automatically reload them for future sessions. The package was developed to make it easier to set up new simulation models — model step templates reduce the need for custom code and make settings more portable between models.

## Project scope

**Status:** Active

**Mission:** UrbanSim Templates provides reusable, configurable model-step
templates and the ModelManager registry for building Orca-based simulation
models from declarative settings rather than custom code.

**Architecture:** UrbanSim Templates is a portable Python layer over Orca,
UrbanSim, and ChoiceModels. Each template encapsulates the data preparation,
estimation, and simulation logic for one kind of model step, and persists its
settings and estimated parameters in portable configuration files. Those files,
rather than pickled Python objects, are the interface through which model steps
are reloaded, shared, and executed by other compatible engines.

The project maintains and develops:

- templates for regression, binary logit, and multinomial logit model steps;
- templates for loading, saving, and deriving data tables and columns;
- the ModelManager registry for saving, reloading, and running model steps;
- shared utilities for data access, filtering, and output handling; and
- portable configuration formats for estimated model steps.

Development of new templates and configuration-format improvements is welcome
within this mission and architecture. Material changes to the project's
mission or execution architecture are considered through UDST's
organization-level governance process.

See the [UDST Project Directory](https://github.com/UDST/.github/blob/main/PROJECTS.md)
for organization-wide project status and policy.

### Installation
UrbanSim Templates can be installed using the Pip or Conda package managers.

```
pip install urbansim_templates
```

```
conda install urbansim_templates --channel conda-forge
```

### Documentation

See the online documentation for much more: https://udst.github.io/urbansim_templates

Some additional documentation is available within the repo in `CHANGELOG.md`, `CONTRIBUTING.md`, `/docs/README.md`, and `/tests/README.md`.

There's discussion of current and planned features in the [pull requests](https://github.com/udst/urbansim_templates/pulls?utf8=✓&q=is%3Apr) and [issues](https://github.com/udst/urbansim_templates/issues?utf8=✓&q=is%3Aissue), both open and closed.
