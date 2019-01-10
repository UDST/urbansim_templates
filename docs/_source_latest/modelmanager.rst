ModelManager API
================

ModelManager runs as an extension to the `Orca <https://udst.github.io/orca>`__ task orchestrator. ModelManager can register template-based model steps with the orchestrator, save them to disk, and automatically reload them for future sessions.

The recommended way to load ModelManager is like this::

    from urbansim_templates import modelmanager
    
    modelmanager.initialize()


Core operations
---------------

.. automodule:: urbansim_templates.modelmanager
   :members: initialize, register, list_steps, get_step, remove_step


Internal functionality
----------------------

These functions are the building blocks of ModelManager. You probably won't need to use 
them directly, but they could be useful for debugging or for extending ModelManager's  
functionality.

.. automodule:: urbansim_templates.modelmanager
   :members: template, build_step, save_step_to_disk, load_supplemental_object, 
             save_supplemental_object, remove_supplemental_object, get_config_dir