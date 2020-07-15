[![Build Status](https://travis-ci.org/UDST/urbansim_templates.svg?branch=master)](https://travis-ci.org/UDST/urbansim_templates)
[![Coverage Status](https://coveralls.io/repos/github/UDST/urbansim_templates/badge.svg?branch=master)](https://coveralls.io/github/UDST/urbansim_templates?branch=master)
[![Docs Status](https://readthedocs.org/projects/urbansim_templates/badge/?version=latest)](https://docs.udst.org/projects/urbansim-templates/en/latest)

# UrbanSim Templates

UrbanSim Templates is a Python library that provides building blocks for Orca-based simulation models. It's part of the [Urban Data Science Toolkit](https://docs.udst.org) (UDST).

The library contains templates for common types of model steps, plus a tool called ModelManager that runs as an extension to the [Orca](https://udst.github.io/orca) task orchestrator. ModelManager can register template-based model steps with the orchestrator, save them to disk, and automatically reload them for future sessions. The package was developed to make it easier to set up new simulation models — model step templates reduce the need for custom code and make settings more portable between models.

### Installation
UrbanSim Templates can be installed using the Pip or Conda package managers. With Conda, you (currently) need to install UrbanSim separately; Pip will handle this automatically.

```
pip install urbansim_templates
```

```
conda install urbansim_templates --channel conda-forge
conda install urbansim --channel udst
```

### Documentation

See the online documentation for much more: https://urbansim-templates.readthedocs.io

Some additional documentation is available within the repo in `CHANGELOG.md`, `CONTRIBUTING.md`, `/docs/README.md`, and `/tests/README.md`.

There's discussion of current and planned features in the open and closed [Pull requests](https://github.com/udst/urbansim_templates/pulls?utf8=✓&q=is%3Apr) and [Issues](https://github.com/udst/urbansim_templates/issues?utf8=✓&q=is%3Aissue).
