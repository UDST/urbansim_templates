Data template APIs
==================

Data templates help you set up model steps for loading data into `Orca <https://udst.github.io/orca>`__ or saving outputs to disk. 

These templates follow the same principles as the statistical model steps. For example, to set up a data table, create an instance of the ``LoadTable`` class and set some properties: the table name, file type, path, and anything else that's needed. 

Registering this object with ModelManager will save it to disk as a yaml file, and create an Orca step with instructions to set up the table. "Running" the object/step registers the table with Orca, but doesn't read the data from disk yet — Orca loads data lazily as it's needed.

Data registration steps are run automatically when you initialize ModelManager.


Loading data
------------

.. autoclass:: urbansim_templates.data.LoadTable
   :members:


Saving data
-----------

.. autoclass:: urbansim_templates.data.SaveTable
   :members:
