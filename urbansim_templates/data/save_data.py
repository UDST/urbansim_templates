from __future__ import print_function

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__


@modelmanager.template
class SaveData():
    """
    Class for saving Orca tables to local CSV or HDF5 files.
    
    All the parameters can also be set as properties after creating the class instance.
    
    Parameters
    ----------
    table : str, optional
        Name of the Orca table. Must be provided before running the step.
    
    columns : str or list of str, optional
        Names of columns to include, in addition to indexes. "None" will return all 
        columns. 
    
    output_type : 'csv' or 'hdf', optional
        Type of file to be created. Must be provided before running the step. 
    
    path : str, optional
        Local file path to save the data to, either absolute or relative to the 
        ModelManager config directory. Please provide a Unix-style path (this will work 
        on any platform, but a Windows-style path won't, and they're hard to normalize 
        automatically). For dynamic file names, you can include the characters ``%RUN%``,
        ``%ITER%``, or ``%TS%``. These will be replaced by the model run number, the 
        iteration value, or a timestamp when the output file is created.
    
    extra_settings : dict, optional
        Additional arguments to pass to `pd.to_csv()` or `pd.to_hdf()`. For example, you
        could automatically compress csv data using {'compression': 'gzip'}, or specify 
        a custom table name for an hdf store using {'key': 'table-name'}. See Pandas 
        documentation for additional settings.
            
    name : str, optional
        Name of the model step.
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    """
    def __init__(self, 
            table = None,
            columns = None,
            output_type = None, 
            path = None, 
            extra_settings = {}, 
            name = None,
            tags = []):
        
        # Template-specific params
        self.table = table
        self.columns = columns
        self.output_type = output_type
        self.path = path
        self.extra_settings = extra_settings
        
        # Standard params
        self.name = name
        self.tags = tags
        
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
            table = d['table'], 
            columns = d['columns'], 
            output_type = d['output_type'], 
            path = d['path'], 
            extra_settings = d['extra_settings'], 
            name = d['name'], 
            tags = d['tags'], 
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
            'table': self.table,
            'columns': self.columns,
            'output_type': self.output_type,
            'path': self.path,
            'extra_settings': self.extra_settings,
        }
        return d
    
    
    def run(self):
        """
        Save a table to disk.
        
        Adding a table to an HDF store requires providing a ``key`` that will be used to 
        identify the table in the store. We'll use the Orca table name, unless you 
        provide a different ``key`` in the ``extra_settings``.

        Returns
        -------
        None
        
        """
        if self.output_type not in ['csv', 'hdf']:
            raise ValueError("Please provide an output type of 'csv' or 'hdf'")
        
        if self.table is None:
            raise ValueError("Please provide the table name")
        
        if self.path is None:
            raise ValueError("Please provide a file path")
        
        kwargs = self.extra_settings
        df = orca.get_table(self.table).to_frame(self.columns)
        
        if self.output_type == 'csv':
            df.to_csv(self.path, **kwargs)
        
        elif self.output_type == 'hdf':
            if 'key' not in kwargs:
                kwargs['key'] = self.table
            
            df.to_hdf(self.path, **kwargs)
        
        