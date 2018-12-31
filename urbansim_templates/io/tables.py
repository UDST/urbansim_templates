from __future__ import print_function

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__


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
    Create an empty class instance: `t = Table()`.
    
    Give it some properties: `t.name = 'buildings'` etc. (These can also be passed when 
    you create the object.)
    
    Register with ModelManager: `modelmanager.register(t)`. This registers the table 
    loading instructions, runs them, and saves them to disk. They'll automatically be run 
    the next time you initialize ModelManager.
    
    You can use all the standard ModelManager commands to get copies of the saved table 
    loading instructions, modify them, and delete them:
    
    - `modelmanager.list_steps()`
    - `t2 = modelmanager.get_step('name')`
    - `modelmanager.register(t2)`
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
        Passed to `orca.add_table()`.
    
    cache_scope : 'step', 'iteration', or 'forever', optional
        Passed to `orca.add_table()`.
    
    copy_col : bool, optional
        Passed to `orca.add_table()`.
        
    name : str, optional
        Name of the table, for Orca. This will also be used as the name of the model step 
        that generates the table. 
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    autorun : bool, optional (default True)
        Automatically run the step whenever it's registered with ModelManager.
    
    Properties and attributes
    -------------------------
    All the parameters listed above can also be get and set as properties of the class 
    instance.
    
    """
    def __init__(self, 
            source_type = None, 
            path = None, 
            csv_index_cols = None,
            csv_settings = None, 
            cache = None, 
            cache_scope = None, 
            copy_col = None, 
            name = None,
            tags = [], 
            autorun = True):
        
        # Template-specific params
        self.source_type = source_type
        self.path = path
        self.csv_index_cols = csv_index_cols
        self.csv_settings = csv_settings
        self.cache = cache
        self.cache_scope = cache_scope
        self.copy_col = copy_col
        
        # Standard params
        self.name = name
        self.tags = tags
        self.autorun = autorun
        
        # Automated params
        self.template = self.__class__.__name__
        self.template_version = __version__
    
    
    @classmethod
    def from_dict(cls, d):
        """
        Create an object instance from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        Table
        
        """
        obj = cls(
            source_type = d['source_type'],
            path = d['path'],
            csv_index_cols = d['csv_index_cols'],
            csv_settings = d['csv_settings'],
            cache = d['cache'],
            cache_scope = d['cache_scope'],
            copy_col = d['copy_col'],
            name = d['name'],
            tags = d['tags'],
            autorun = d['autorun']
        )
        return obj
    
    
    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Returns
        -------
        dict
        
        """
        d = {
            'template': self.template,
            'template_version': self.template_version,
            'name': self.name,
            'tags': self.tags,
            'autorun': self.autorun,
            'source_type': self.source_type,
            'path': self.path,
            'csv_index_cols': self.csv_index_cols,
            'csv_settings': self.csv_settings,
            'cache': self.cache,
            'cache_scope': self.cache_scope,
            'copy_col': self.copy_col
        }
        return d
    
    
    def validate(self):
        """
        Check some basic expectations about the table generated by the step:
        
        - Confirm that the table includes a unique, named index column (primary key) or 
          set of columns (composite key). If not, raise a ValueError.
        
        - If the table contains columns whose names match the index columns of tables
          previously registered with Orca, check whether they make sense as join keys.
          If the presumptive foreign-key columns include values not found in the 
          primary key columns, print a warning.
        
        - Perform the same check for columns in previously registered tables whose names
          match the index of the table generated by this step.
          
        Running this will load all registered Orca tables into memory (if they have not 
        yet been loaded), which may take a while.
        
        Returns
        -------
        bool
        
        """
        # Register table if needed
        if not orca.is_table(self.name):
            self.run()
        
        idx = orca.get_table(self.name).index
        
        # Check index has a name
        if list(idx.names) == [None]:
            raise ValueError("Index column has no name")
        
        # Check index is unique
        if len(idx.unique()) < len(idx):    
            raise ValueError("Index not unique")
    
    
    def run(self):
        """
        Register a data table with Orca.
        
        Returns
        -------
        None
        
        """
        if self.source_type == 'csv':
            @orca.table(table_name = self.name, 
                        cache = self.cache, 
                        cache_scope = self.cache_scope, 
                        copy_col=self.copy_col)
            def orca_table():
                df = pd.read_csv(self.path).set_index(self.csv_index_cols)
                return df
            
        
        