import re

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__
from urbansim_templates.shared import CoreTemplateSettings, OutputColumnSettings
from urbansim_templates.utils import get_df


@modelmanager.template
class ColumnFromExpression():
    """
    Template to register a column of derived data with Orca, based on an expression. The 
    column will be associated with an existing table. Values will be calculated lazily, 
    only when the column is needed for a specific operation. 
    
    The expression will be passed to ``df.eval()`` and can refer to any columns in the 
    same table. See the Pandas documentation for further details.
    
    Parameters can be passed to the constructor or set as attributes.
    
    Parameters
    ----------
    meta : :mod:`~urbansim_templates.shared.CoreTemplateSettings`, optional
        Stores a name for the configured template and other standard settings. For
        column templates, the default for 'autorun' is True.
    
    table : str, optional
        Name of the Orca table the column will be associated with. Required before 
        running.
    
    expression : str, optional
        String describing operations on existing columns of the table, for example 
        "a/log(b+c)". Required before running. Supports arithmetic and math functions 
        including sqrt, abs, log, log1p, exp, and expm1 -- see Pandas ``df.eval()`` 
        documentation for further details.
    
    output : :mod:`~urbansim_templates.shared.OutputColumnSettings`, optional
        Stores settings for the column that will be generated.
        
    """
    def __init__(self,
            meta = None,
            table = None,
            expression = None,
            output = None):
        
        if meta is None:
            self.meta = CoreTemplateSettings(autorun=True)
        
        self.meta.template = self.__class__.__name__
        self.meta.template_version = __version__
                
        # Template-specific settings
        self.table = table
        self.expression = expression
        
        if output is None:
            self.output = OutputColumnSettings()
    

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
            meta = d['meta'],
            table = d['table'],
            expression = d['expression'],
            output = d['output'],
        )
        return obj
    
    
    @classmethod
    def from_dict_0_2_dev5(cls, d):
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
            'meta': self.meta.to_dict(),
            'table': self.table,
            'expression': self.expression,
            'output': self.output.to_dict(),
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
        if self.output.column_name is None:
            raise ValueError("Please provide a column name")
        
        table = self.table if self.output.table is None else self.output.table
        
        if table is None:
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
        
        @orca.column(table_name = table, 
                     column_name = self.output.column_name, 
                     cache = self.output.cache, 
                     cache_scope = self.output.cache_scope)
        def orca_column():
            df = get_df(table, columns=cols)
            series = df.eval(self.expression)
            
            if self.output.missing_values is not None:
                series = series.fillna(self.output.missing_values)
            
            if self.output.data_type is not None:
                series = series.astype(self.output.data_type)
            
            return series
        
    