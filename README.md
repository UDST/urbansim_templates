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

- Each substantive PR should increment the developer build number of the library, e.g. `0.1.dev0` -> `0.1.dev1`. The production release at the end of this sequence would be `0.1`, which would be followed by `0.2.dev0`. The library version number is saved in any yaml files a user creates, for troubleshooting and managing format changes.

   The version number needs to be updated in both `/setup.py` and `/urbansim_templates/__init__.py`. See further discussion in [issue #35](https://github.com/UDST/urbansim_templates/issues/35).

- Each PR writeup should carefully document the changes it includes -- especially any changes to the API or file storage format -- so that we can put together good release notes. This codebase will soon have many users.

- A template is a Python class that conforms to the following spec:

   1. can save itself to a dict  
   2. can rebuild itself from a dict using a method named `from_dict()`  
   3. can execute a configured version of itself using a method named `run()`  
   4. can register itself with `modelmanager` using a method named `register()`
   5. accepts "name" and "tags" parameters

- ModelManager (`/urbansim_templates/modelmanager.py`) handles saving and reloading of configured template instances, aka model steps. It also registers them as Orca objects. 

- Running a configured model step executes logic and typically saves output to Orca.

- Templates should try to use parameter names that are consistent or harmonious with other templates.

- Data tables should be input as named Orca objects. Other inputs that are hard to store as strings (like callables) should probably be input as Orca objects as well; we're still working on a solution for this.

- All template parameters should be accepted either as constructor parameters or object properties, if feasible:

    ```py
    m1 = TemplateStep(foo='yes')
    m2 = TemplateStep()
    m2.foo = 'yes'
    ```

- It's fine for templates to require interactive configuration, like fitting a statistical model. Also fine to require these actions to be completed before the model step can be saved or run.

- Ideally, users should be able to edit object properties and re-run the interactive components whenever they like. Changes will not be saved until a an object is re-registered with ModelManager.

- Lightweight intermediate outputs like summary tables and fitted parameters should be saved in an object's dictionary representation if feasible.

- It can be helpful to save more complex intermediate outputs to the class object so that users can access them (e.g. which observations were sampled, what the fitted probabilities are, etc) -- but we don't have a solution right now for saving these to disk.

- Shared template logic is in `shared.py` for now, but it's not very elegant. No need for templates to extend the `TemplateStep` class unless it's helpful.

- Each new template class needs to be imported by name into `modelmanager.py`, for now. See discussion [here](https://github.com/UDST/urbansim_templates/blob/master/urbansim_templates/modelmanager.py#L105-L114).

- We don't have design patterns yet for templates whose final output is to _generate_ DataFrames or Series, rather than modifying existing ones, but this is a high priority.
