from __future__ import print_function

import datetime

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__
from urbansim_templates.utils import get_data


@modelmanager.template
class SaveTable():
    """
    Template for saving Orca tables to local CSV or HDF5 files. Parameters can be passed
    to the constructor or set as attributes.
    
    Parameters
    ----------
    table : str, optional
        Name of the Orca table. Must be provided before running the step.
    
    columns : str or list of str, optional
        Names of columns to include. ``None`` will return all columns. Indexes will 
        always be included.
    
    filters : str or list of str, optional
        Filters to apply to the data before saving. Will be passed to 
        ``pd.DataFrame.query()``.
    
    output_type : 'csv' or 'hdf', optional
        Type of file to be created. Must be provided before running the step. 
    
    path : str, optional
        Local file path to save the data to, either absolute or relative to the 
        ModelManager config directory. Please provide a Unix-style path (this will work 
        on any platform, but a Windows-style path won't, and they're hard to normalize 
        automatically). For dynamic file names, you can include the characters "%RUN%",
        "%ITER%", or "%TS%". These will be replaced by the run id, the model iteration 
        value, or a timestamp when the output file is created.
    
    extra_settings : dict, optional
        Additional arguments to pass to ``pd.to_csv()`` or ``pd.to_hdf()``. For example, 
        you could automatically compress csv data using {'compression': 'gzip'}, or 
        specify a custom table name for an hdf store using {'key': 'table-name'}. See 
        Pandas documentation for additional settings.
            
    name : str, optional
        Name of the model step.
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    """
    def __init__(self, 
            table = None,
            columns = None,
            filters = None,
            output_type = None, 
            path = None, 
            extra_settings = None, 
            name = None,
            tags = []):
        
        # Template-specific params
        self.table = table
        self.columns = columns
        self.filters = filters
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
            filters = d['filters'], 
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
            'filters': self.filters,
            'output_type': self.output_type,
            'path': self.path,
            'extra_settings': self.extra_settings,
        }
        return d
    
    
    def get_dynamic_filepath(self):
        """
        Substitute run id, model iteration, and/or timestamp into the filename. 
        
        For the run id and model iteration, we look for Orca injectables named ``run_id`` 
        and ``iter_var``, respectively. If none is found, we use ``0``.
        
        The timestamp is UTC, formatted as ``YYYYMMDD-HHMMSS``.
        
        Returns
        -------
        str
        
        """
        if self.path is None:
            raise ValueError("Please provide a file path")

        run = 0
        if orca.is_injectable('run_id'):
            run = orca.get_injectable('run_id')
        
        iter = 0
        if orca.is_injectable('iter_var'):
            iter = orca.get_injectable('iter_var')
        
        ts = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        
        s = self.path
        s = s.replace('%RUN%', str(run))
        s = s.replace('%ITER%', str(iter))
        s = s.replace('%TS%', ts)
        
        return s
    
    
    def run(self):
        """
        Save a table to disk.
        
        Saving a table to an HDF store requires providing a ``key`` that will be used to 
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
        if kwargs is None:
            kwargs = dict()

        df = get_data(tables = self.table, 
                      filters = self.filters, 
                      extra_columns = self.columns)
                
        if self.output_type == 'csv':
            df.to_csv(self.get_dynamic_filepath(), **kwargs)
        
        elif self.output_type == 'hdf':
            if 'key' not in kwargs:
                kwargs['key'] = self.table
            
            df.to_hdf(self.get_dynamic_filepath(), **kwargs)
        
        