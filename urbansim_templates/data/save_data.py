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
    output_type : 'csv' or 'hdf', optional
        This is required to save the table, but does not have to be provided when the 
        object is created.
    
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
        Name of the Orca table. HOW TO NAME THE MODEL STEP?
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    """
    def __init__(self, 
            output_type = None, 
            path = None, 
            extra_settings = {}, 
            name = None,
            tags = []):
        
        # Template-specific params
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
            'output_type': self.output_type,
            'path': self.path,
            'extra_settings': self.extra_settings,
        }
        return d
    
    
    def run(self):
        """
        
        ``pd.to_hdf()`` requires a ``key`` to identify the table in the HDF store. We'll 
        use the Orca table name for this, unless you provide a different ``key`` in the
        ``extra_settings``.

        Returns
        -------
        None
        
        """
        if self.output_type not in ['csv', 'hdf']:
            raise ValueError("Please provide an output type of 'csv' or 'hdf'")
        
        if self.name is None:
            raise ValueError("Please provide the table name")
        
        if self.path is None:
            raise ValueError("Please provide a file path")
        
        kwargs = self.extra_settings
        df = orca.get_table(self.name).to_frame()
        
        if self.output_type == 'csv':
            df.to_csv(self.path, **kwargs)
        
        elif self.output_type == 'hdf':
            if 'key' not in kwargs:
                kwargs['key'] = self.name
            
            df.to_hdf(self.path, **kwargs)
        
        