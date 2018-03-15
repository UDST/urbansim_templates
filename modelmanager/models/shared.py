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
                

    @classmethod
    def from_dict(cls, d):
        """
        Create an object instance from a saved dictionary representation. 
        
        Child classes will need to override this method to implement loading of custom
        parameters and estimation results. 
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        TemplateStep
        
        """
        return cls(d['tables'], d['model_expression'], d['filters'], d['out_tables'],
                d['out_column'], d['out_transform'], d['out_filters'], d['name'],
                d['tags'])
    
    
    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Child classes will need to override this method to implement saving of custom
        parameters and estimation results.
        
        Returns
        -------
        dict
        
        """
        d = {
            'type': self.type,
            'name': self.name,
            'tags': self.tags,
            'tables': self.tables,
            'model_expression': self.model_expression,
            'filters': self.filters,
            'out_tables': self.out_tables,
            'out_column': self.out_column,
            'out_transform': self.out_transform
        }
        return d
    
    
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
        expression or filters, plus (it appears) the index of each merged table. Relevant 
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


    def _get_out_column(self):
        """
        Return name of the column to save data to. This is 'out_column' if it exsits,
        otherwise the left-hand-side column name from the model expression.
        
        Returns
        -------
        str
        
        """
        if self.out_column is not None:
            return self.out_column
        
        else:
            # TO DO - there must be a cleaner way to get LHS column name
            return self.model_expression.split('~')[0].split(' ')[0]
    
    
    def _get_out_table(self):
        """
        Return name of the table to save data to. This is 'out_tables' or its first 
        element, if it exists, otherwise 'tables' or its first element.
        
        Returns
        -------
        str
        
        """
        if self.out_tables is not None:
            tables = self.out_tables
        else:
            tables = self.tables
            
        if isinstance(tables, str):
            return tables
        else:
            return tables[0]
        
    
    def _generate_name(self):
        """
        Generate a name based on the class name and a timestamp.
        
        Returns
        -------
        str
        
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
