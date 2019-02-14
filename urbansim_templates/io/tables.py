from __future__ import print_function

import os

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__


@modelmanager.template
class TableFromDisk():
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
    Create an empty class instance: `t = TableFromDisk()`.
    
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
        Local file path to load data from, either absolute or relative to the 
        ModelManager config directory. Path will be normed at runtime using 
        `os.path.normpath()`, so either a Unix-style or Windows-style path should work 
        across platforms.
    
    url : str, optional
        Remote url to download file from, NOT YET IMPLEMENTED.
    
    csv_index_cols : str or list of str, optional
        Required for csv source type.
    
    csv_settings : dict, optional
        Additional arguments to pass to `pd.read_csv()`. For example, you can  
        automatically extract data from a gzip file using {'compression': 'gzip'}. See 
        Pandas documentation for additional settings.
    
    hdf_key : str, optional
        Name of table to read from the HDF5 file, if there are multiple.
    
    filters : str or list of str, optional
        Filters to apply before registering the table with Orca.
        
        TO DO - IMPLEMENT
    
    orca_test_spec : dict, optional
        Data characteristics to be tested when the table is validated, NOT YET 
        IMPLEMENTED.
    
    cache : bool, optional
        Passed to `orca.table()`. Note that the default is `True`, unlike in the 
        underlying general-purpose Orca function, because tables read from disk should 
        not need to be regenerated during the course of a model run.
    
    cache_scope : 'step', 'iteration', or 'forever', optional
        Passed to `orca.table()`. Default is 'forever', as in Orca.
    
    copy_col : bool, optional
        Passed to `orca.table()`. Default is `True`, as in Orca. 
        
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
            cache = True, 
            cache_scope = 'forever', 
            copy_col = True, 
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
        
        # Automatic params
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
    
    
    def run(self):
        """
        Register a data table with Orca.
        
        Returns
        -------
        None
        
        """
        if self.source_type is None:
            raise ValueError("Please provide a source type")
        
        if self.name is None:
            raise ValueError("Please provide a table name")
        
        if self.path is None:
            raise ValueError("Please provide a file path")
        
        if self.source_type == 'csv':
            @orca.table(table_name = self.name, 
                        cache = self.cache, 
                        cache_scope = self.cache_scope, 
                        copy_col=self.copy_col)
            def orca_table():
                path = os.path.normpath(self.path)
                kwargs = self.csv_settings
                df = pd.read_csv(path, **kwargs).set_index(self.csv_index_cols)
                return df
            
        
    def validate(self):
        """
        Check some basic expectations about the table generated by the step:
        
        - Confirm that the table includes a unique, named index column (primary key) or 
          set of columns (composite key). If not, raise a ValueError.
        
        - If the table contains columns whose names match the index columns of tables
          previously registered with Orca, check whether they make sense as join keys.
          Print a status message with the number of presumptive foreign-key values that 
          are found in the primary key column. 
        
        - Perform the same check for columns in previously registered tables whose names
          match the index of the table generated by this step.
          
        - It doesn't currently compare indexes to indexes. (Maybe it should?)
          
        Running this will trigger loading all registered Orca tables into memory, which 
        may take a while if they have not yet been loaded. Stand-alone columns will not 
        be loaded unless their names match an index column. 
        
        Returns
        -------
        bool
        
        """
        # There are a couple of reasons we're not using the orca_test library here:
        # (a) orca_test doesn't currently support MultiIndexes, and (b) the primary-key/
        # foreign-key comparisons aren't asserting anything, just printing status 
        # messages. We should update orca_test to support both, probably.
        
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
        
        # Compare columns to indexes of other tables, and vice versa
        combinations = [(self.name, t) for t in orca.list_tables() if self.name != t] \
                + [(t, self.name) for t in orca.list_tables() if self.name != t]
        
        for t1, t2 in combinations:
            col_names = orca.get_table(t1).columns
            idx = orca.get_table(t2).index
            
            if set(idx.names).issubset(col_names):
                vals = orca.get_table(t1).to_frame(idx.names).drop_duplicates()
                
                # Easier to compare multi-column values to multi-column index if we 
                # turn the values into an index as well
                vals = vals.reset_index().set_index(idx.names).index
                vals_in_idx = sum(vals.isin(idx))
                
                if len(idx.names) == 1:
                    idx_str = idx.names[0]
                else:
                    idx_str = '[{}]'.format(','.join(idx.names))
                
                print("'{}.{}': {} of {} unique values are found in '{}.{}' ({}%)"\
                        .format(t1, idx_str, 
                                vals_in_idx, len(vals), 
                                t2, idx_str, 
                                round(100*vals_in_idx/len(vals))))
    
        return True
    
    
        