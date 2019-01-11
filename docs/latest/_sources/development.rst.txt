Development guide
=================

Below are some strategies we've come up with for the templates. Technical contribution guidelines are in the `Github repo <http://github.com/UDST/urbansim_templates/blob/master/CONTRIBUTING.md>`__.


Design patterns for templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A ModelManager-compliant template is a Python class that conforms to the following spec:

   1. can save itself to a dict using a method named ``to_dict()``
   2. can rebuild itself from a dict using a method named ``from_dict()``
   3. can execute a configured version of itself using a method named ``run()``
   4. accepts parameters ``name`` (str) and ``tags`` (list of str)
   5. uses the ``@modelmanager.template`` decorator

Running a configured model step executes logic and typically saves output to Orca.

Templates should try to use parameter names that are consistent or harmonious with other templates.

Tables and columns of data should be input as named Orca objects. Other inputs that are hard to store as strings (like callables) should probably be input as Orca objects as well; we're still working on a solution for this.

All template inputs should be accepted either as constructor parameters or object properties, if feasible:

.. code-block:: python

    m1 = TemplateStep(foo='yes')
    m2 = TemplateStep()
    m2.foo = 'yes'

It's fine for templates to require interactive configuration, like fitting a statistical model. Also fine to require these actions to be completed before the model step can be saved or run.

Ideally, users should be able to edit object properties and re-run the interactive components whenever they like. Changes will not be saved until a an object is re-registered with ModelManager.

Lightweight intermediate outputs like summary tables and fitted parameters should be saved in an object's dictionary representation if feasible.

Bigger intermediate outputs, like pickled copies of full fitted models, can be automatically stored to disk by providing an entry named ``supplemental_objects`` in a model's dictionary representation. This should contain a list of dicts, each of which has parameters ``name`` (str), ``content`` (obj), and ``content_type`` (str, e.g. 'pickle').

To avoid dependency bloat, the default installation only includes the dependencies required for core model management and the most commonly used templates. Templates using additional libraries should check whether they're installed before fitting or running a model step, and provide helpful error messages if not. 
