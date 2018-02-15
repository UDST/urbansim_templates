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

# Additionally, models loaded from disk remain fully interactive objects that can be
# examined, copied, and edited.

model2 = mm.get_model('name')
```

Without ModelManager, the equivalent workflow would be to estimate a model, generate a config file for it, write a function in `models.py` to register it with Orca, and edit it by modifying the config file or creating a replacement.

ModelManager works directly with the current versions of [UrbanSim](https://github.com/udst/urbansim) and [Orca](https://github.com/udst/orca), and is fully interoperable with existing projects and model steps. 


### How it works

ModelManager-compliant model step classes need to implement the following features:

1. Ability to save themselves to a dictionary (a `to_dict()` method)

2. Ability to rebuild themselves from a dictionary (a `from_dict()` [class method](http://stackabuse.com/pythons-classmethod-and-staticmethod-explained/))

(ModelManager will handle conversion of the dictionaries to/from YAML or some other future storage format.)

3. Ability to run themselves (e.g. a `run()` method)

If you look in the `models` directory you'll see an OLS model step class called `RegressionStep` that adds these features to the existing UrbanSim regression model class. Similar code can be written for other kind of model steps!

The `modelmanager.py` file implements centralized saving and loading of the dictionaries. 

In an UrbanSim project directory, steps saved by ModelManager will show up in a file called `modelmanager_configs.yaml`.


### Installation

```sh
git clone https://github.com/urbansim/modelmanager.git
cd modelmanager; python setup.py develop
```


### User's guide

Demo notebook: [REPM estimation.ipynb](https://github.com/urbansim/parcel_template_sandbox/blob/master/notebooks/REPM%20estimation.ipynb)

Choose a directory for your project, ideally an existing UrbanSim project since ModelManager cannot yet load data into Orca on its own.

For building and registering model steps, use: 

```py
from modelmanager.models import RegressionStep
```

For loading or inspecting previously saved model steps, use:

```py
import modelmanager as mm
```

For example, adding `import modelmanager` to the top of a file like `simulation.py` will automatically give Orca access to all previously saved steps in a given project directory.

Please refer to the ModelManager python files for details of the API. 


### Developer's guide


### Roadmap

- tests
- binary logit (Arezoo?)
- multinomial logit (Max?)