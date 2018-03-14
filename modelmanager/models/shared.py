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
        

    @classmethod
    def from_dict(cls, d):
        """
        Create an object instance from a saved dictionary representation. Child classes
        will need to implement saving and loading of parameter esimates and any other
        custom data. 
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        TemplateStep or child class
        
        """
        return cls(d['tables'], d['model_expression'], d['filters'], d['out_tables'],
                d['cout_column'], d['out_transform'], d['out_filters'], d['name'],
                d['tags'])
    
    
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
        Generate a data table for estimation or prediction, relying on functionality from
        Orca and UrbanSim.models.util. This should be performed immediately before 
        estimation or prediction so that it reflects the current data state.
        
        The output includes only the necessary columns: those mentioned in the model
        expression and filters, plus (it appears) the index of each merged table. Relevant 
        filter queries are applied.
        
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
            
            filters = self.filters
        
        elif (task == 'predict'):
            if self.out_tables is not None:
                tables = self.out_tables
            else:
                tables = self.tables
                
            columns = util.columns_in_formula(self.model_expression) \
                    + util.columns_in_filters(self.out_filters)
            
            if self.out_column is not None:
                columns += [self.out_column]
            
            filters = self.out_filters
        
        if isinstance(tables, list):
            df = orca.merge_tables(target=tables[0], tables=tables, columns=columns)
        else:
            df = orca.get_table(tables).to_frame(columns)
            
        df = util.apply_filter_query(df, filters)
        return df


    def _generate_name(self):
        """
        Generate a name based on the class name and a timestamp.
        
        """
        return self.type + '-' + dt.now().strftime('%Y%m%d-%H%M%S')

    
    def run(self):
        """
        Execute the model step. Child classes are required to implement this method.
        
        """
        return
        
    
    def register(self):
        """
        Register the model step with Orca and the ModelManager. This includes saving it
        to disk so it will be automatically loaded in the future. 
        
        """
        d = self.to_dict()
        mm.add_step(d)
