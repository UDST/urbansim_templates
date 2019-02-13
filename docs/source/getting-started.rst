Getting started
===============

Intro
-----

UrbanSim Templates is a Python library that provides building blocks for Orca-based simulation models. It's part of the `Urban Data Science Toolkit <http://docs.udst.org>`__ (UDST).

The library contains templates for common types of model steps, plus a tool called ModelManager that runs as an extension to the `Orca <https://udst.github.io/orca>`__ task orchestrator. ModelManager can register template-based model steps with the orchestrator, save them to disk, and automatically reload them for future sessions. The package was developed to make it easier to set up new simulation models — model step templates reduce the need for custom code and make settings more portable between models.

UrbanSim Templates is `hosted on Github <https://github.com/udst/urbansim_templates>`__ with a BSD 3-Clause open source license. The code repository includes some material not found in this documentation: a `change log <https://github.com/UDST/urbansim_templates/blob/master/CHANGELOG.md>`__, a `contributor's guide <http://>`__, and instructions for `running the tests <https://github.com/UDST/urbansim_templates/blob/master/tests/README.md>`__, `updating the documentation <http://>`__, and `creating a new release <http://>`__.

Another useful resource is the `issues <https://github.com/UDST/urbansim_templates/issues?utf8=✓&q=is%3Aissue>`__ and `pull requests <https://github.com/UDST/urbansim_templates/pulls?q=is%3Apr>`__ on Github, which include detailed feature proposals and other discussions.

UrbanSim Templates was created in 2018 by Sam Maurer (maurer@urbansim.com), who remains the lead developer, with contributions from Paul Waddell, Max Gardner, Eddie Janowicz, Arezoo Besharati Zadeh, Xavier Gitiaux, and others.


Installation
------------

UrbanSim Templates is tested with Python versions 2.7, 3.5, 3.6, and 3.7. 

As of Feb. 2019, there is an installation problem in Python 3.7 when using Pip (because of an issue with Orca's PyTables dependency). Conda should work.

.. note::
    It can be helpful to set up a dedicated Python environment for each project you work on. This lets you use a stable and replicable set of libraries that won't be affected by other projects. Here are some good `environment settings <https://gist.github.com/smmaurer/f3a4f424a4aa877fb73e1cb2567bd89d>`__ for UrbanSim Templates projects.
    
Production releases
~~~~~~~~~~~~~~~~~~~

UrbanSim Templates can be installed using the Pip or Conda package managers. With Conda, you (currently) need to install UrbanSim separately; Pip will handle this automatically.

.. code-block:: python

    pip install urbansim_templates

.. code-block:: python

    conda install urbansim_templates --channel conda-forge
    conda install urbansim --channel udst

Dependencies include `NumPy <http://numpy.org>`__, `Pandas <http://pandas.pydata.org>`__, and `Statsmodels <http://statsmodels.org>`__, plus two other UDST libraries: `Orca <http://udst.github.io/orca>`__ and `ChoiceModels <http://github.com/udst/choicemodels>`__. These will be included automatically when you install UrbanSim Templates. 

Certain less-commonly-used templates require additional packages: currently, `PyLogit <https://github.com/timothyb0912/pylogit>`__ and `Scikit-learn <http://scikit-learn.org>`__. You'll need to install these manually to use the associated templates. 

When new production releases of UrbanSim Templates come out, you can upgrade like this:

.. code-block:: python

    pip install urbansim_templates --upgrade

.. code-block:: python

    conda update urbansim_templates --channel conda-forge


Developer pre-releases
~~~~~~~~~~~~~~~~~~~~~~

Developer pre-releases of UrbanSim Templates can be installed using the Github URL. These versions sometimes require having a developer release of `ChoiceModels <http://github.com/udst/choicemodels>`__ as well. Information about the developer releases can be found in Github `pull requests <https://github.com/UDST/urbansim_templates/pulls?q=is%3Apr>`__.

.. code-block:: python

    pip install git+git://github.com/udst/choicemodels.git
    pip install git+git://github.com/udst/urbansim_templates.git

You can use the same command to upgrade.


Cloning the repository
~~~~~~~~~~~~~~~~~~~~~~

If you'll be modifying the code, you can install UrbanSim Templates by cloning the Github repository:

.. code-block:: python

    git clone https://github.com/udst/urbansim_templates.git
    cd urbansim_templates
    python setup.py develop

Update it with ``git pull``.


Basic usage
-----------

Initializing ModelManager
~~~~~~~~~~~~~~~~~~~~~~~~~

To get started, import and initialize ModelManager. This makes sure there's a directory set up to store any template-based model steps that are generated within the script or notebook. 

.. code-block:: python

    from urbansim_templates import modelmanager
    
    modelmanager.initialize()

The default file location is a ``configs`` folder located in the current working directory; you can provide an alternate path if needed. If ModelManager finds existing saved objects in the directory, it will load them and register them with Orca.

.. note::
    It can be helpful to add a cell to your notebook that reports which version of UrbanSim Templates is installed, particularly if you're using development releases!
    
    .. code-block:: python
    
        In [2]: import urbansim_templates
                print(urbansim_templates.__version__)
        
        Out[2]: '0.1.dev12'


Creating a model step
~~~~~~~~~~~~~~~~~~~~~

Now we can choose a template and use it to build a model step. The templates are Python classes that contain logic for setting up and running different kinds of model logic — currently focusing on OLS regressions and discrete choice models.

A template takes a variety of arguments, which can either be passed as parameters or set as object properties after an instance of the template is created. 

.. code-block:: python

    from urbansim_templates.models import OLSRegressionStep
    
    m = OLSRegressionStep()
    m.name = 'price-prediction'
    m.tables = 'buildings'
    m.model_expression = 'sale_price ~ residential_sqft'

This sets up ``m`` as an instance of the OLS regression template. The ``tables`` and ``model_expression`` arguments refer to data that needs to be registered separately with Orca. So let's load the data before trying to estimate the model: 

.. code-block:: python
    
    import orca
    import pandas as pd
    
    url = "https://www.dropbox.com/s/vxg5pdfzxrh6osz/buildings-demo.csv?dl=1"
    df = pd.read_csv(url).dropna()
    orca.add_table('buildings', df)


Fitting the statistical model
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now we can fit the building price model:

.. code-block:: python
    
    m.fit()

This will print a summary table describing the estimation results. 

Now that we have a fitted model, we can use it to predict sale prices for other buildings. UrbanSim forecasting models consist of many interconnected steps like this, iteratively predicting real estate prices, household moves, construction, and other urban dynamics. 


Registering the step
~~~~~~~~~~~~~~~~~~~~

Now we can register the model step:

.. code-block:: python

    modelmanager.register(m)

ModelManager parses the step, saves a copy to disk, and registers a runnable version of it as a standard Orca step, so that it can be invoked as part of a sequence of other steps:

.. code-block:: python

    orca.run(['price-prediction', 'household-moves', 'residential-development'])

In real usage, some additional parameters would be set to specify which data to use for prediction, and where to store the output.


Making changes
~~~~~~~~~~~~~~

ModelManager also includes some interactive functionality. Previously registered steps can be retrieved as template objects, which can be modified and re-registered as needed. This also works with model steps loaded from disk.

.. code-block:: python

    modelmanager.list_steps()
    
    m2 = modelmanager.get_step('price-prediction')
    ...
    
    m2.name = 'better-price-prediction'
    modelmanager.register(m2)
    modelmanager.remove_step('price-prediction')
    
If you take a look in the ``configs`` folder, you'll see a yaml file representing the saved model step. It includes the settings we provided, plus the fitted coefficients and anything else generated by the internal logic of the template.
