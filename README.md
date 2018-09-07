# UrbanSim Templates

UrbanSim Templates defines a common structure for new model steps and provides a core set of flexible templates and related tools. The goal is to enable smoother model setup, easier code reuse, and improvements to task orchestration. 

The library has two main components. `urbansim_templates.modelmanager` serves as an extension to Orca, handling saving, loading, and registration of template-based model steps. `urbansim_templates.models` contains class definitions for a core set of pre-defined templates. Some of the statistics functionality comes from our [ChoiceModels](https://github.com/UDST/choicemodels/) library, also in active development.

UrbanSim Templates is currently in pre-release. API documentation is in the Python code ([modelmanager](https://github.com/UDST/urbansim_templates/blob/master/urbansim_templates/modelmanager.py), [models](https://github.com/UDST/urbansim_templates/tree/master/urbansim_templates/models)). There's additional discussion in the [issues](https://github.com/UDST/urbansim_templates/issues?utf8=✓&q=is%3Aissue) and in recently merged [pull requests](https://github.com/UDST/urbansim_templates/pulls?utf8=✓&q=is%3Apr). 


### Installation

You can follow the setup instructions in [UAL/urbansim_parcel_bayarea](https://github.com/ual/urbansim_parcel_bayarea) to create a conda environment with everything you need for working in the UrbanSim Templates ecosystem.

If you already have most of it installed, this should be sufficient:

```
git clone https://github.com/udst/urbansim_templates.git
cd urbansim_templates
python setup.py develop
```


### Bug reports

Open an issue, or contact Sam (maurer@urbansim.com).


### Usage overview

[Initialization-demo.ipynb](https://github.com/ual/urbansim_parcel_bayarea/blob/master/general-notebooks/Initialization-demo.ipynb)

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


### Design patterns for template development

- Let's keep the master branch clean and runnable. To make fixes or add features, create a new branch, and open a pull request when you're ready to merge code into master. Have someone else review it before merging, if possible.

- A template should be a Python class that can (a) save itself to a dict, (b) rebuild itself from a dict using a method named `from_dict()`, (c) run itself using a method named `run()`, and (d) register itself with `modelmanager` using a method named `register()`.

