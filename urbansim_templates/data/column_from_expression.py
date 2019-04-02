import re

import orca
import pandas as pd

from urbansim_templates import modelmanager, __version__
from urbansim_templates.shared import CoreTemplateSettings, OutputColumnSettings
from urbansim_templates.utils import get_df


class ExpressionSettings():
    """
    Stores custom parameters used by the ColumnFromExpression template. Parameters can be
    passed to the constructor or set as attributes.
    
    Parameters
    ----------
    table : str, optional
        Name of Orca table the expression will be evaluated on. Required before running
        then template.
    
    expression : str, optional
        String describing operations on existing columns of the table, for example 
        "a/log(b+c)". Required before running. Supports arithmetic and math functions 
        including sqrt, abs, log, log1p, exp, and expm1 -- see Pandas ``df.eval()`` 
        documentation for further details.
    
    """
    def __init__(self, table = None, expression = None):
        self.table = table
        self.expression = expression
    
    @classmethod
    def from_dict(cls, d):
        return cls(table=d['table'], expression=d['expression'])

    def to_dict(self):
        return {'table': self.table, 'expression': self.expression}


@modelmanager.template
class ColumnFromExpression():
    """
    Template to register a column of derived data with Orca, based on an expression. The 
    column will be associated with an existing table. Values will be calculated lazily, 
    only when the column is needed for a specific operation. 
    
    The expression will be passed to ``df.eval()`` and can refer to any columns in the 
    same table. See the Pandas documentation for further details.
    
    Parameters
    ----------
    meta : :mod:`~urbansim_templates.shared.CoreTemplateSettings`, optional
        Standard parameters. This template sets the default value of ``meta.autorun``
        to True.
    
    data : :mod:`~urbansim_templates.data.ExpressionSettings`, optional
        Special parameters for this template.
        
    output : :mod:`~urbansim_templates.shared.OutputColumnSettings`, optional
        Parameters for the column that will be generated. This template uses
        ``data.table`` as the default value for ``output.table``.
        
    """
    def __init__(self, meta=None, data=None, output=None):
        
        self.meta = CoreTemplateSettings(autorun=True) if meta is None else meta
        self.meta.template = self.__class__.__name__
        self.meta.template_version = __version__
                
        self.data = ExpressionSettings() if data is None else data
        self.output = OutputColumnSettings() if output is None else output
    

    @classmethod
    def from_dict(cls, d):
        
        if 'meta' not in d:
            return ColumnFromExpression.from_dict_0_2_dev5(d)
        
        return cls(
            meta = CoreTemplateSettings.from_dict(d['meta']),
            data = ExpressionSettings.from_dict(d['data']),
            output = OutputColumnSettings.from_dict(d['output']))    
    
    
    @classmethod
    def from_dict_0_2_dev5(cls, d):
        """
        Converter to read saved data from 0.2.dev5 or earlier.
        
        """
        return cls(
            column_name = d['column_name'],
            table = d['table'],
            expression = d['expression'],
            data_type = d['data_type'],
            missing_values = d['missing_values'],
            cache = d['cache'],
            cache_scope = d['cache_scope'],
            name = d['name'],
            tags = d['tags'],
            autorun = d['autorun'])
    
    
    def to_dict(self):
        return {
            'meta': self.meta.to_dict(), 
            'data': self.data.to_dict(),
            'output': self.output.to_dict()}
    
    
    def run(self):
        """
        Run the template, registering a column of derived data with Orca.
        
        Requires values to be set for ``data.table``, ``data.expression``, and
        ``output.column_name``.
        
        """
        table = self.data.table if self.output.table is None else self.output.table
        
        if table is None:
            raise ValueError("Please provide a table")
        
        if self.data.expression is None:
            raise ValueError("Please provide an expression")
        
        if self.output.column_name is None:
            raise ValueError("Please provide a column name")
        
        # Some column names in the expression may not be part of the core DataFrame, so 
        # we'll need to request them from Orca explicitly. This regex pulls out column 
        # names into a list, by identifying tokens in the expression that begin with a 
        # letter and contain any number of alphanumerics or underscores, but do not end 
        # with an opening parenthesis. This will also pick up constants, like "pi", but  
        # invalid column names will be ignored when we request them from get_df().
        cols = re.findall('[a-zA-Z_][a-zA-Z0-9_]*(?!\()', self.data.expression)
        
        @orca.column(table_name = table, 
                     column_name = self.output.column_name, 
                     cache = self.output.cache, 
                     cache_scope = self.output.cache_scope)
        def orca_column():
            df = get_df(table, columns=cols)
            series = df.eval(self.data.expression)
            
            if self.output.missing_values is not None:
                series = series.fillna(self.output.missing_values)
            
            if self.output.data_type is not None:
                series = series.astype(self.output.data_type)
            
            return series
        
    