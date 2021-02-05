Shared utilities
================

The utilities are mainly helper functions for templates. 


General template tools API
--------------------------

.. automodule:: urbansim_templates.shared
   :members: CoreTemplateSettings


Column output tools API
-----------------------

.. automodule:: urbansim_templates.shared
   :members: OutputColumnSettings, register_column


Table schemas and merging API
-----------------------------

.. automodule:: urbansim_templates.utils
   :members: validate_table, validate_all_tables, merge_tables


Other helper functions API
--------------------------

.. automodule:: urbansim_templates.utils
   :members: all_cols, cols_in_expression, get_data, get_df, trim_cols, to_list, update_column, update_name


Spec validation API
-------------------

.. automodule:: urbansim_templates.utils
   :members: validate_template


Version management API
----------------------

.. automodule:: urbansim_templates.utils
   :members: parse_version, version_greater_or_equal
