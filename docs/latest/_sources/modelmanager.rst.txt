ModelManager API
================

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