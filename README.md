[![Build Status](https://travis-ci.org/UDST/urbansim_templates.svg?branch=master)](https://travis-ci.org/UDST/urbansim_templates)
[![Coverage Status](https://coveralls.io/repos/github/UDST/urbansim_templates/badge.svg?branch=master)](https://coveralls.io/github/UDST/urbansim_templates?branch=master)

# UrbanSim Templates

UrbanSim Templates defines a common structure for new model steps and provides a core set of flexible templates and related tools. The goal is to enable smoother model setup, easier code reuse, and improvements to task orchestration. 

The library has two main components. `urbansim_templates.modelmanager` serves as an extension to Orca, handling saving, loading, and registration of template-based model steps. `urbansim_templates.models` contains class definitions for a core set of pre-defined templates. Some of the statistics functionality comes from our [ChoiceModels](https://github.com/UDST/choicemodels/) library, also in active development.

UrbanSim Templates is currently in pre-release. API documentation is in the Python code ([modelmanager](https://github.com/UDST/urbansim_templates/blob/master/urbansim_templates/modelmanager.py), [models](https://github.com/UDST/urbansim_templates/tree/master/urbansim_templates/models)). There's additional discussion in the [issues](https://github.com/UDST/urbansim_templates/issues?utf8=✓&q=is%3Aissue) and in recently merged [pull requests](https://github.com/UDST/urbansim_templates/pulls?utf8=✓&q=is%3Apr). 


## Installation

You can install UrbanSim Templates from pip or conda (NOT YET - COMING SOON!) or by cloning the Github repository.

We recommend using the [Anaconda Python distribution](https://www.anaconda.com/download/) and setting up a dedicated Python environment for your UrbanSim Templates projects. This makes it easier to replicate software environments across machines and easier to diagnose dependency problems.

UrbanSim Templates requires UDST packages [Orca](https://github.com/udst/orca), [ChoiceModels](https://github.com/udst/choicemodels), and [UrbanSim](https://github.com/udst/urbansim), plus third-party packages NumPy, Pandas, Patsy, and Statsmodels. These will all be set up automatically when you install UrbanSim Templates.

Certain less-commonly-used templates require additional packages: currently, PyLogit and Scikit-Learn. Running the unit tests requires PyTest, Coveralls, and Coverage. Other packages that can be useful for UrbanSim projects include Matplotlib, Pandana, GeoPandas, SciPy, line_profiler, memory_profiler, and nb_conda_kernels.


### Production releases

Coming soon to pip and conda.

### Development releases

The latest development release can be installed using the Github URL. These currently require having a development release of ChoiceModels as well, which you should install first.

```
pip install git+git://github.com/udst/choicemodels.git
pip install git+git://github.com/udst/urbansim_templates.git
```

### Cloning the repository

If you will be editing the library code or frequently updating to newer development versions, you can clone the repository and link it to your Python environment:

```
git clone https://github.com/udst/urbansim_templates.git
cd urbansim_templates
python setup.py develop
```

## Bug reports

Open an issue, or contact Sam (maurer@urbansim.com).


## Usage overview

[Initialization-demo.ipynb](https://github.com/UDST/public-template-workspace/blob/master/notebooks-sam/2018-07-initialization-demo.ipynb)

UrbanSim Templates treats model steps as _objects you can interact with_, rather than just functions with inputs and outputs. This enables some nice workflows, such as registration of model steps without needing to add them to a `models.py` file:

```py
from urbansim_templates import modelmanager
from urbansim_templates.models import OLSRegressionStep

modelmanager.initialize()

model = OLSRegressionStep(<parameters>)
model.fit()
modelmanager.register(model)

# The model step is now registered with Orca and saved to disk. ModelManager tracks and
# loads all previously saved steps, just as if they were listed in models.py.

orca.run(['name'])

# If needed, the previously saved steps can be re-loaded into class instances that can be 
# examined, copied, and edited.

model2 = modelmanager.get_model('name')
```

Prior to ModelManager, the equivalent workflow would be to (1) estimate a model, (2) generate a config file for it, (3) write a function in `models.py` to register it with Orca, and (4) edit it by modifying the config file or creating a replacement.

ModelManager works directly with the current versions of [UrbanSim](https://github.com/udst/urbansim) and [Orca](https://github.com/udst/orca), and is fully interoperable with existing UrbanSim projects and model steps. 


## Design patterns for template development

- Let's keep the master branch of this library clean and runnable. To make fixes or add features, create a new branch, and open a pull request when you're ready to merge code into master. Have someone else review it before merging, if possible. There's a writeup of our general Git workflow [over here](https://github.com/ual/urbansim_parcel_bayarea/wiki/Git-workflows-and-tips).

- Each substantive PR should increment the developer build number of the library, e.g. `0.1.dev0` -> `0.1.dev1`. The production release at the end of this sequence would be `0.1`, which would be followed by `0.2.dev0`. 

   This versioning style is sometimes called "major.minor.micro with development releases" ([PEP 440](https://www.python.org/dev/peps/pep-0440/)). The version number is included in saved yaml files, for troubleshooting and managing format changes.

   Note that the version number needs to be updated in both `/setup.py` and `/urbansim_templates/__init__.py`. See further discussion in [issue #35](https://github.com/UDST/urbansim_templates/issues/35).

- Each PR writeup should carefully document the changes it includes -- especially any changes to the API or file storage format -- so that we can put together good release notes. This codebase will soon have many users.

- A template is a Python class that conforms to the following spec:

   1. can save itself to a dict using a method named `to_dict()`  
   2. can rebuild itself from a dict using a method named `from_dict()`  
   3. can execute a configured version of itself using a method named `run()`  
   4. accepts parameters `name` (str) and `tags` (list of str)
   5. uses the `@modelmanager.template` decorator

- ModelManager (`/urbansim_templates/modelmanager.py`) handles saving and reloading of configured template instances, aka model steps. It also registers them as Orca objects. 

- Running a configured model step executes logic and typically saves output to Orca.

- Templates should try to use parameter names that are consistent or harmonious with other templates.

- Data tables should be input as named Orca objects. Other inputs that are hard to store as strings (like callables) should probably be input as Orca objects as well; we're still working on a solution for this.

- All template inputs should be accepted either as constructor parameters or object properties, if feasible:

    ```py
    m1 = TemplateStep(foo='yes')
    m2 = TemplateStep()
    m2.foo = 'yes'
    ```

- It's fine for templates to require interactive configuration, like fitting a statistical model. Also fine to require these actions to be completed before the model step can be saved or run.

- Ideally, users should be able to edit object properties and re-run the interactive components whenever they like. Changes will not be saved until a an object is re-registered with ModelManager.

- Lightweight intermediate outputs like summary tables and fitted parameters should be saved in an object's dictionary representation if feasible.

- Bigger intermediate outputs, like pickled copies of full fitted models, can be automatically stored to disk by providing an entry named `supplemental_objects` in a model's dictionary representation. This should contain a list of dicts, each of which has parameters `name` (str), `content` (obj), and `content_type` (str, e.g. 'pickle').

- Shared template functionality is in `utils.py`. There's also a `TemplateStep` parent class in `shared.py`, but this hasn't worked very well; see [issue #38](https://github.com/UDST/urbansim_templates/issues/38).

- We don't have design patterns yet for templates whose final output is to _generate_ DataFrames or Series, rather than modifying existing ones, but we're working on it.

- To avoid dependency bloat, the default installation only includes the external libraries required for core model management and the most commonly used templates. Templates using additional libraries should check whether they're installed before fitting or running a model step, and provide helpful error messages if not. 
