# UrbanSim_Templates

ModelManager is a small extension to UrbanSim that treats model steps as _objects you can interact with_, rather than just functions with inputs and outputs. This enables some nice workflows, such as registration of model steps without needing to add them to a `models.py` file:

```py
from urbansim_templates import modelmanager as mm
from urbansim_templates.models import OLSRegressionStep

model = OLSRegressionStep('name', parameters)
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

#### Where's the code?

If you look in the [models](https://github.com/UDST/urbansim_templates/tree/master/urbansim_templates/models) directory you'll see an OLS model step class called `OLSRegressionStep` that implements these features on top of an existing UrbanSim regression model class. 

The [modelmanager.py](https://github.com/UDST/urbansim_templates/blob/master/urbansim_templates/modelmanager.py) file handles centralized saving and loading of the configs. 

#### Where are model steps saved to?

In an UrbanSim project directory, the steps saved by ModelManager will show up in a file called `modelmanager_configs.yaml`.


## Installation

```
git clone https://github.com/udst/urbansim_templates.git
cd urbansim_templates
python setup.py develop
```


## User's guide

Demo notebook: [Demo.ipynb](https://github.com/ual/urbansim_parcel_bayarea/blob/master/notebooks-sam/Demo.ipynb)

Choose a directory to work in, ideally an existing UrbanSim project since ModelManager cannot yet load data into Orca on its own.

For building and registering model steps, use: 

```py
from urbansim_templates.models import OLSRegressionStep
```

For loading or inspecting previously saved model steps, use:

```py
from urbansim_templates import modelmanager as mm
```

For example, adding `import urbansim_templates` to the top of a file like `simulation.py` will automatically give Orca access to all previously saved steps in the same project directory.

Please refer to the Python files for details of the current API. 


## Developer's guide

Let's keep the master branch clean and runnable. To make fixes or add features, create a new branch, and open a pull request when you're ready to merge code into master. Have someone else review it before merging, if possible.


## Roadmap

Here's a rough development wish list. See issues for more details, and feel free to claim an issue or open new ones.

#### Infrastructure:

- integration with Jupyter Lab in the cloud
- unit tests and continuous integration hooks
- documentation, releases, distribution details

#### Features:

- `datamanager.py` to support loading data and generating computed columns using a similar workflow (Sam M) 
- various TO DO items in the code
- class for network aggregation model steps
- classes for transition steps and other loose ends
- class for developer model if feasible

#### Applications:

- notebooks demonstrating how to set up each piece of a model

