from __future__ import print_function

try:
    import pathlib  # Python 3.4+
except:
    pass

import os

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__


@modelmanager.template
class LoadData():
    """
    Class for registering data tables from local CSV or HDF5 files.
    
    An instance of this template class stores *instructions for loading a data table*, 
    packaged into an Orca step. Running the instructions registers the table with Orca. 
    Saved table registration steps will be run automatically when you initialize 
    ModelManager, replacing the ``datasources.py`` scripts used in previous versions of 
    UrbanSim. 
    
    Tables should include a unique index, or a set of columns that jointly represent a 
    unique index. 
    
    If a column has the same name as the index of another table, ModelManager expects to 
    be able to use it as a join key. Following these naming conventions eliminates the 
    need for Orca "broadcasts".
    
    All the parameters can also be set as properties after creating the class instance.
    
    Parameters
    ----------
    source_type : 'csv' or 'hdf', optional
        This is required to load the table, but does not have to be provided when the 
        object is created.
    
    path : str, optional
        Local file path to load data from, either absolute or relative to the 
        ModelManager config directory. The string you provide will immediately be 
        normalized to a platform-agnostic format, using `os.path.normpath()` in Python 2 
        or `pathlib.Path()` in Python 3. It is always safe to provide a Unix-style path, 
        and you may provide a Windows-style path if you are creating the model step in 
        Windows. Saved steps will run on any platform. 
    
    url : str, optional - NOT YET IMPLEMENTED
        Remote url to download file from.
    
    csv_index_cols : str or list of str, optional
        Required for csv source type.
    
    extra_settings : dict, optional
        Additional arguments to pass to `pd.read_csv()` or `pd.read_hdf()`. For example, 
        you could automatically extract csv data from a gzip file using {'compression': 
        'gzip'}, or specify the table identifier within a multi-object hdf store using 
        {'key': 'table-name'}. See Pandas documentation for additional settings.
    
    filters : str or list of str, optional - NOT YET IMPLEMENTED
        Filters to apply before registering the table with Orca.
    
    orca_test_spec : dict, optional - NOT YET IMPLEMENTED
        Data characteristics to be tested when the table is validated.
    
    cache : bool, default True
        Passed to `orca.table()`. Note that the default is `True`, unlike in the 
        underlying general-purpose Orca function, because tables read from disk should 
        not need to be regenerated during the course of a model run.
    
    cache_scope : 'step', 'iteration', or 'forever', default 'forever'
        Passed to `orca.table()`. Default is 'forever', as in Orca.
    
    copy_col : bool, default True
        Passed to `orca.table()`. Default is `True`, as in Orca. 
        
    name : str, optional
        Name of the table, for Orca. This will also be used as the name of the model step 
        that generates the table. 
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    autorun : bool, default True
        Automatically run the step whenever it's registered with ModelManager.
    
    """
    def __init__(self, 
            source_type = None, 
            path = None, 
            csv_index_cols = None,
            extra_settings = {}, 
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
        self.extra_settings = extra_settings
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
            extra_settings = d['extra_settings'],
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
            'extra_settings': self.extra_settings,
            'cache': self.cache,
            'cache_scope': self.cache_scope,
            'copy_col': self.copy_col
        }
        return d
    
    
    @property
    def path(self):
        return self.__path
    @path.setter
    def path(self, value):
        if value is not None:
            try:
                value = str(pathlib.Path(value))  # Python 3.4+
            except:
                value = os.path.normpath(value)
        self.__path = value
            

    def run(self):
        """
        Register a data table with Orca.
        
        Requires values to be set for ``source_type``, ``name``, and ``path``. CSV data 
        also requires ``csv_index_cols``. 
        
        Returns
        -------
        None
        
        """
        if self.source_type not in ['csv', 'hdf']:
            raise ValueError("Please provide a source type of 'csv' or 'hdf'")
        
        if self.name is None:
            raise ValueError("Please provide a table name")
        
        if self.path is None:
            raise ValueError("Please provide a file path")
        
        kwargs = self.extra_settings
        
        # Table from CSV file
        if self.source_type == 'csv':
            if self.csv_index_cols is None:
                raise ValueError("Please provide index column name(s) for the csv")
        
            @orca.table(table_name = self.name, 
                        cache = self.cache, 
                        cache_scope = self.cache_scope, 
                        copy_col = self.copy_col)
            def orca_table():
                df = pd.read_csv(self.path, **kwargs).set_index(self.csv_index_cols)
                return df
            
        # Table from HDF file
        elif self.source_type == 'hdf':
            @orca.table(table_name = self.name, 
                        cache = self.cache, 
                        cache_scope = self.cache_scope, 
                        copy_col = self.copy_col)
            def orca_table():
                df = pd.read_hdf(self.path, **kwargs)
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
    
    