# UrbanSim Templates

UrbanSim Templates defines a common structure for new model steps and provides a core set of flexible templates and related tools. The goal is to enable smoother model setup, easier code reuse, and improvements to task orchestration. 

The library has two main components. `urbansim_templates.modelmanager` serves as an extension to Orca, handling saving, loading, and registration of template-based model steps. `urbansim_templates.models` contains class definitions for a core set of pre-defined templates.

UrbanSim Templates is currently in pre-release. API documentation is in the docstrings ([modelmanager](https://github.com/UDST/urbansim_templates/blob/master/urbansim_templates/modelmanager.py), [models](https://github.com/UDST/urbansim_templates/tree/master/urbansim_templates/models)). There's additional discussion in the [issues](https://github.com/UDST/urbansim_templates/issues?utf8=✓&q=is%3Aissue) and in recently merged [pull requests](https://github.com/UDST/urbansim_templates/pulls?utf8=✓&q=is%3Apr). Usage examples coming soon. Please feel free to reach out by email or by opening an issue, if you have questions or bug reports!

Lead developer: Sam Maurer, maurer@berkeley.edu


## Workflow overview

UrbanSim Templates treats model steps as _objects you can interact with_, rather than just functions with inputs and outputs. This enables some nice workflows, such as registration of model steps without needing to add them to a `models.py` file:

```py
from urbansim_templates import modelmanager as mm
from urbansim_templates.models import OLSRegressionStep

mm.initialize()

model = OLSRegressionStep(<parameters>)
model.fit()
model.register()

# The model step is now registered with Orca and saved to disk. ModelManager tracks and
# loads all previously saved steps, just as if they were listed in models.py.

orca.run(['name'])

# If needed, the previously saved steps can be re-loaded into class instances that can be 
# examined, copied, and edited.

model2 = mm.get_model('name')
```

Prior to ModelManager, the equivalent workflow would be to (1) estimate a model, (2) generate a config file for it, (3) write a function in `models.py` to register it with Orca, and (4) edit it by modifying the config file or creating a replacement.

ModelManager works directly with the current versions of [UrbanSim](https://github.com/udst/urbansim) and [Orca](https://github.com/udst/orca), and is fully interoperable with existing UrbanSim projects and model steps. 


## Long-term vision

The goal with this is to make it easier to develop UrbanSim templates -- combinations of data schemas and model steps that we can use in multiple projects without requiring too much customization. 

The ModelManager workflow will streamline rollout of a template: once the data is in place, we can estimate and validate model steps by walking through pre-filled Jupyter Notebooks.

There are side benefits as well: easier experimentation with model specifications, easier benchmarking and comparison of alternative model flows (including future hooks for auto-specification), and hopefully easier interoperability with GUI components.

The tradeoff is that model steps from a template class will not be as flexible as general-purpose Orca steps. But since there is a lot of commonality among UrbanSim implementations, it should get us pretty far.


## How it works

To work with ModelManager, a model step class needs to implement the following features:

1. Ability to save itself to a dictionary (a `to_dict()` method)

2. Ability to rebuild itself from a dictionary (a `from_dict()` [class method](http://stackabuse.com/pythons-classmethod-and-staticmethod-explained/))

(ModelManager will handle conversion of the dictionaries to/from YAML or some other future storage format.)

3. Ability to run itself (e.g. a `run()` method)

4. Ability to register itself with ModelManager (a `register()` method) -- just a single line of code, implemented by combining the prior three capabilities


## Installation

```
git clone https://github.com/udst/urbansim_templates.git
cd urbansim_templates
python setup.py develop
```


## Developer guide

Let's keep the master branch clean and runnable. To make fixes or add features, create a new branch, and open a pull request when you're ready to merge code into master. Have someone else review it before merging, if possible.


