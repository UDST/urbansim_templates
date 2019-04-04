Data management templates
=========================

Usage
-----

Data templates help you load tables into `Orca <https://udst.github.io/orca>`__, create columns of derived data, or save tables or subsets of tables to disk. 

.. code-block:: python
    
    from urbansim_templates.data import LoadTable
    
    t = LoadTable()
    t.table = 'buildings'  # a name for the Orca table
    t.source_type = 'csv'
    t.path = 'buildings.csv'
    t.csv_index_cols = 'building_id'
    t.name = 'load_buildings'  # a name for the model step that sets up the table

You can run this directly using ``t.run()``, or register the configured template to be part of a larger workflow:

.. code-block:: python

    from urbansim_templates import modelmanager

    modelmanager.register(t)

Registration does two things: (a) it saves the configured template to disk as a yaml file, and (b) it creates a model step with logic for loading the table. Running the model step is equivalent to running the configured template object:

.. code-block:: python

    t.run()
    
    # equivalent:
    import orca
    orca.run(['load_buildings'])

Strictly speaking, running the model step doesn't load the data, it just sets up an Orca table with instructions for loading the data when it's needed. (This is called lazy evaluation.)

.. code-block:: python

    orca.run(['load_buildings'])  # now an Orca table named 'buildings' is registered
    
    orca.get_table('buildings').to_frame()  # now the data is read from disk

Because "running" the table-loading step is costless, it's done automatically when you register a configured template. It's also done automatically when you initialize a ModelManager session and table-loading configs are read from yaml. (If you'd like to disable this for a particular table, you can set ``t.autorun == False``.)


Recommended data schemas
~~~~~~~~~~~~~~~~~~~~~~~~

The :mod:`~urbansim_templates.data.LoadTable` template will work with any data that can be loaded into a Pandas DataFrame. But we highly recommend following stricter data schema rules:

1. Each table should include a unique, named index column (a.k.a. primary key) or set of columns (multi-index, a.k.a composite key).

2. If a column is meant to be a join key for another table, it should have the same name as the index of that table.

3. Duplication of column names across tables (except for the join keys) is discouraged, for clarity. 

If you follow these rules, tables can be automatically merged on the fly, for example to assemble estimation data or calculate indicators.

You can use :func:`~urbansim_templates.utils.validate_table()` or :func:`~urbansim_templates.utils.validate_all_tables()` to check whether these expectations are met. When templates merge tables on the fly, they use :func:`~urbansim_templates.utils.merge_tables()`.

These utility functions work with any Orca table that meets the schema expectations, whether or not it was created with a template.


Compatibility with Orca
~~~~~~~~~~~~~~~~~~~~~~~

From Orca's perspective, tables set up using the :mod:`~urbansim_templates.data.LoadTable` template are equivalent to tables that are registered using ``orca.add_table()`` or the ``@orca.table`` decorator. Technically, they are ``orca.TableFuncWrapper`` objects.

Unlike the templates, Orca relies on user-specified "`broadcast <http://udst.github.io/orca/core.html#merge-api>`__" relationships to perform automatic merging of tables. :mod:`~urbansim_templates.data.LoadTable` does not register any broadcasts, because they're not needed if tables follow the schema rules above. So if you use these tables in non-template model steps, you may need to add broadcasts separately.


Data loading API
----------------

.. currentmodule:: urbansim_templates.data

.. autosummary::
    LoadTable

.. autoclass:: urbansim_templates.data.LoadTable
   :members:


Column creation API
-------------------

.. currentmodule:: urbansim_templates.data

.. autosummary::
    ColumnFromExpression
    ExpressionSettings

.. autoclass:: urbansim_templates.data.ColumnFromExpression
   :members:

.. autoclass:: urbansim_templates.data.ExpressionSettings
   :members:

Data output API
---------------

.. currentmodule:: urbansim_templates.data

.. autosummary::
    SaveTable

.. autoclass:: urbansim_templates.data.SaveTable
   :members:


