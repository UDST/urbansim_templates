from __future__ import print_function

import orca

from urbansim_templates import modelmanager


@modelmanager.template
class Table():
    """
    Class for registering data tables. In the initial implementation, data can come from  
    local CSV or HDF5 files.
    
    An instance of this Table() template stores *instructions for loading a data table*, 
    which can be saved as a yaml file. Running these instructions registers the table 
    with Orca. Saved tables will be registered automatically when you initialize 
    ModelManager, replacing the `datasources.py` scripts used in previous versions of 
    UrbanSim. 
    
    Tables should include a unique index, or a set of columns that jointly represent a 
    unique index. 
    
    If a column has the same name as the index of another table, ModelManager expects to 
    be able to use it as a join key. Following these naming conventions eliminates the 
    need for Orca "broadcasts".
    
    Usage
    -----
    Create an empty class instance: `m = Table()`.
    
    Give it some properties: `m.name = 'buildings'` etc. (These can also be passed when 
    you create the object.)
    
    Register with ModelManager: `modelmanager.register(m)`. This registers the table 
    loading instructions, runs them, and saves them to disk. They'll automatically be run 
    the next time you initialize ModelManager.
    
    You can use all the standard ModelManager commands to get copies of the saved table 
    loading instructions, modify them, and delete them:
    
    - `modelmanager.list_steps()`
    - `m2 = modelmanager.get_step('name')`
    - `modelmanager.register(m2)`
    - `modelmanager.remove_step('name')`
    
    Parameters
    ----------
    source_type : 'csv' or 'hdf', optional
        This is required to load the table, but does not have to be provided when the 
        object is created.
    
    path : str, optional
        Local file path, either absolute or relative to the ModelManager config directory.
        
        TO DO - CROSS PLATFORM SUPPORT?
    
    url : str, optional
        Remote url to download file from, NOT YET IMPLEMENTED.
    
    csv_index_cols : str or list of str, optional
        Required for csv source type.
    
    csv_settings : dict, optional
        Additional parameters to pass to `pd.read_csv()`.
    
    hdf_key : str, optional
        Name of table to read from the HDF5 file, if there are multiple.
    
    zipped : bool, optional
        Whether the source file is zipped, NOT YET IMPLEMENTED.
    
    path_in_archive : str, optional
        NOT YET IMPLEMENTED.
    
    filters : str or list of str, optional
        Filters to apply before registering the table with Orca.
        
        TO DO - IMPLEMENT
    
    orca_test_spec : dict, optional
        Data characteristics to be tested when the table is validated, NOT YET 
        IMPLEMENTED.
    
    cache : bool, optional
        Orca table setting (DEFAULT?).
    
    cache_scope : ??, optional
        Orca table setting.
    
    copy_col : ??, optional
        Orca table setting.
        
    name : str, optional
        Name of the table, for Orca. This will also be used as the name of the model step 
        that generates the table. 
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    autorun : bool, optional
        Automatically "run" the step with the parameters passed to the constructor. This 
        will be set to True in dict representations of the object, so that loading it 
        into ModelManager will automatically register the table with Orca. 
    
    Properties and attributes
    -------------------------
    All the parameters listed above can also be get and set as properties of the class 
    instance.
    
    """
    def __init__(self):
        pass
    
    
    @classmethod
    def from_dict(cls, d):
        pass
    
    def to_dict(self):
        pass
    
    
    def validate(self):
        pass
    
    
    def run(self):
        pass