from __future__ import print_function

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__


@modelmanager.template
class ColumnFromExpression():
    """
    Template to register a column of derived data with Orca, based on an expression. The 
    column will be associated with an existing table. Values will be calculated lazily, 
    only when the column is requested for a specific operation. 
    
    The expression will be passed to ``pd.eval()`` and can refer to other columns in the 
    same table. See the Pandas documentation for further details.
    
    All the parameters can also be set as properties after creating the template 
    instance.
    
    Parameters
    ----------
    column_name : str, optional
        Name of the Orca column to be registered. Required before running.
    
    table : str, optional
        Name of the Orca table the column will be associated with. Required before 
        running.
    
    expression : str, optional
        Expression for calculating values of the column. Required before running.
    
    cache : bool, default False
        Whether to cache column values after they are calculated.
    
    cache_scope : 'step', 'iteration', or 'forever', default 'forever'
        How long to cache column values for (ignored if ``cache`` is False).
    
    name : str, optional
        Name of the template instance and associated model step. 
    
    tags : list of str, optional
        Tags to associate with the template instance.
    
    autorun : bool, default True
        Whether to run automatically when the template instance is registered with 
        ModelManager.
    
    """
    def __init__(self, 
            column_name = None, 
            table = None, 
            expression = None, 
            cache = False, 
            cache_scope = 'forever', 
            name = None,
            tags = [], 
            autorun = True):
        
        # Template-specific params
        self.column_name = column_name
        self.table = table
        self.expression = expression
        self.cache = cache
        self.cache_scope = cache_scope
        
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
            column_name = d['column_name'],
            table = d['table'],
            expression = d['expression'],
            cache = d['cache'],
            cache_scope = d['cache_scope'],
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
            'column_name': self.column_name,
            'table': self.table,
            'expression': self.expression,
            'cache': self.cache,
            'cache_scope': self.cache_scope,
        }
        return d
    
    
    def run(self):
        """
        Run the template, registering a column of derived data with Orca.
        
        Requires values to be set for ``column_name``, ``table``, and ``expression``.
        
        Returns
        -------
        None
        
        """
        if self.column_name is None:
            raise ValueError("Please provide a column name")
        
        if self.table not in ['csv', 'hdf']:
            raise ValueError("Please provide a table")
        
        if self.expression is None:
            raise ValueError("Please provide an expression")
        
        @orca.column(table_name = self.table, 
                     column_name = self.column_name, 
                     cache = self.cache, 
                     cache_scope = self.cache_scope)
        def orca_column():
            pass
        
    