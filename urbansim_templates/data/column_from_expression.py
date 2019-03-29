from __future__ import print_function

import re

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__
from urbansim_templates.utils import get_df


@modelmanager.template
class ColumnFromExpression():
    """
    Template to register a column of derived data with Orca, based on an expression. The 
    column will be associated with an existing table. Values will be calculated lazily, 
    only when the column is requested for a specific operation. 
    
    The expression will be passed to ``df.eval()`` and can refer to other columns in the 
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
        String describing operations on existing columns of the table, for example 
        "a/log(b+c)". Required before running. Supports arithmetic and math functions 
        including sqrt, abs, log, log1p, exp, and expm1 -- see Pandas ``df.eval()`` 
        documentation for further details.
    
    data_type : str, optional
        Python type or ``numpy.dtype`` to cast the column's values into.
    
    missing_values : str or numeric, optional
        Value to use for rows that would otherwise be missing.
    
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
            data_type = None, 
            missing_values = None, 
            cache = False, 
            cache_scope = 'forever', 
            name = None,
            tags = [], 
            autorun = True):
        
        # Template-specific params
        self.column_name = column_name
        self.table = table
        self.expression = expression
        self.data_type = data_type
        self.missing_values = missing_values
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
            data_type = d['data_type'],
            missing_values = d['missing_values'],
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
            'data_type': self.data_type,
            'missing_values': self.missing_values,
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
        
        if self.table is None:
            raise ValueError("Please provide a table")
        
        if self.expression is None:
            raise ValueError("Please provide an expression")
        
        # Some column names in the expression may not be part of the core DataFrame, so 
        # we'll need to request them from Orca explicitly. This regex pulls out column 
        # names into a list, by identifying tokens in the expression that begin with a 
        # letter and contain any number of alphanumerics or underscores, but do not end 
        # with an opening parenthesis. This will also pick up constants, like "pi", but  
        # invalid column names will be ignored when we request them from get_df().
        cols = re.findall('[a-zA-Z_][a-zA-Z0-9_]*(?!\()', self.expression)
        
        @orca.column(table_name = self.table, 
                     column_name = self.column_name, 
                     cache = self.cache, 
                     cache_scope = self.cache_scope)
        def orca_column():
            df = get_df(self.table, columns=cols)
            series = df.eval(self.expression)
            
            if self.missing_values is not None:
                series = series.fillna(self.missing_values)
            
            if self.data_type is not None:
                series = series.astype(self.data_type)
            
            return series
        
    