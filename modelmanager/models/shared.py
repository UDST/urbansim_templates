from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca
from urbansim.models import util

from .. import modelmanager as mm


class TemplateStep(object):
    """
    Shared functionality for the template classes.
    
    Parameters
    ----------
    tables : str or list of str, optional
        Required to fit a model, but doesn't have to be provided at initialization.
    model_expression : str, optional
        Required to fit a model, but doesn't have to be provided at initialization.
    filters : str or list of str ?, optional
        Replaces `fit_filters` argument.
    out_tables : str or list of str, optional
    out_column : str, optional
        Replaces `out_fname` argument.
    out_transform : callable, optional
        Replaces `ytransform` argument.
    out_filters : str or list of str ?, optional
        Replaces `predict_filters` argument.
    name : str, optional
        For ModelManager.
    tags : list of str, optional
        For ModelManager.

    """
    def __init__(self, tables=None, model_expression=None, filters=None, out_tables=None,
            out_column=None, out_transform=None, out_filters=None, name=None, tags=None):
        
        self.tables = tables
        self.model_expression = model_expression
        self.filters = filters
        
        self.out_tables = out_tables
        self.out_column = out_column
        self.out_transform = out_transform
        self.out_filters = out_filters
        
        self.name = name
        self.tags = tags
        
        self.type = type(self).__name__  # class name
        
        # Placeholder for the fitted model
        self.model = None
        
        # It seems fine for users to access and change the above properties directly.
        # If we want to test for acceptable values, a good way to do it would be with
        # @property definitions.

    
    @property
    def tables(self):
        return self.__tables
        

    @tables.setter
    def tables(self, tables):
        """
        Normalize storage of the 'tables' property. TO DO - add type validation?
        
        """
        self.__tables = tables
        
        if isinstance(tables, list):
            # Normalize [] to None
            if len(tables) == 0:
                self.__tables = None
            
            # Normalize [str] to str
            if len(tables) == 1:
                self.__tables = tables[0]
            
    
    @property
    def out_tables(self):
        return self.__out_tables
        

    @out_tables.setter
    def out_tables(self, out_tables):
        """
        Normalize storage of the 'out_tables' property. TO DO - add type validation?
        
        """
        self.__out_tables = out_tables
        
        if isinstance(out_tables, list):
            # Normalize [] to None
            if len(out_tables) == 0:
                self.__out_tables = None
            
            # Normalize [str] to str
            if len(out_tables) == 1:
                self.__out_tables = out_tables[0]


    def _get_data(self, task='fit'):
        """
        Generate a data table for estimation or prediction, from Orca table and column
        names. The results should not be stored, in case the data in Orca changes.
        
        Parameters
        ----------
        task : 'fit' or 'predict'
        
        Returns
        -------
        DataFrame
        
        """
        
        # TO DO - verify tables and model_expression are not None
        
        if (task == 'fit'):
            tables = self.tables
            columns = util.columns_in_formula(self.model_expression) \
                    + util.columns_in_filters(self.filters)
        
        elif (task == 'predict'):
            if not (self.out_tables is None):
                tables = self.out_tables
            else:
                tables = self.tables
                
            columns = util.columns_in_formula(self.model_expression) \
                    + util.columns_in_filters(self.out_filters)
            
            if not (self.out_column is None):
                columns += [self.out_column]
        
        if isinstance(tables, list):
            df = orca.merge_tables(target=tables[0], tables=tables, columns=columns)
        else:
            df = orca.get_table(tables).to_frame(columns)
            
        return df







