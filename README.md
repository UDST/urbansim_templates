# ModelManager

ModelManager is a small extension to UrbanSim that treats model steps as _objects you can interact with_, rather than just functions with inputs and outputs. This enables some nice workflows, such as registration of model steps without needing to add them to a `models.py` file:

```py
import modelmanager as mm
from modelmanager.models import RegressionStep

model = RegressionStep('name', parameters)
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


## How it works

To work with ModelManager, model step classes need to implement the following features:

1. Ability to save themselves to a dictionary (a `to_dict()` method)

2. Ability to rebuild themselves from a dictionary (a `from_dict()` [class method](http://stackabuse.com/pythons-classmethod-and-staticmethod-explained/))

(ModelManager will handle conversion of the dictionaries to/from YAML or some other future storage format.)

3. Ability to run themselves (e.g. a `run()` method)

4. Ability to register themselves with ModelManager (a `register()` method), which is done through a combination of the first three features

#### Where's the code?

If you look in the [models](https://github.com/urbansim/modelmanager/tree/master/modelmanager/models) directory you'll see an OLS model step class called `RegressionStep` that implements these features on top of an existing UrbanSim regression model class. 

The [modelmanager.py](https://github.com/urbansim/modelmanager/blob/master/modelmanager/modelmanager.py) file handles centralized saving and loading of the dictionaries. 

In an UrbanSim project directory, the steps saved by ModelManager will show up in a file called `modelmanager_configs.yaml`.


## Installation

```
git clone https://github.com/urbansim/modelmanager.git
cd modelmanager
python setup.py develop
```


## User's guide

Demo notebook: [REPM estimation.ipynb](https://github.com/urbansim/parcel_template_sandbox/blob/master/notebooks/REPM%20estimation.ipynb)

Choose a directory to work in, ideally an existing UrbanSim project since ModelManager cannot yet load data into Orca on its own.

For building and registering model steps, use: 

```py
from modelmanager.models import RegressionStep
```

For loading or inspecting previously saved model steps, use:

```py
import modelmanager as mm
```

For example, adding `import modelmanager` to the top of a file like `simulation.py` will automatically give Orca access to all previously saved steps in the same project directory.

Please refer to the ModelManager python files for details of the API. 


## Developer's guide

Let's keep the master branch clean and runnable. To make fixes or add features, create a new branch, do the work there, and open a pull request when you're ready to merge code into master. Have someone else review it before merging, if possible.


## Roadmap

Here's a rough development wish list. See issues for more details, and feel free to claim an issue or open new ones.

Infrastructure:
- is there a sample data set following the parcel template schema guidelines, that we can use for testing and development?
- integration with Jupyter Lab in the cloud
- unit tests and continuous integration hooks
- documentation, releases, distribution details (later on)

Features:
- `datamanager.py` to support loading data and generating computed columns using a similar workflow (Sam M) 
- various TO DO items in the code
- class for binary logit model steps (Arezoo?)
- class for multinomial logit model steps (Max?)
- class for network aggregation model steps
- classes for transition steps and other loose ends
- class for developer model if feasible

Applications:
- notebooks demonstrating how to set up each piece of a model

