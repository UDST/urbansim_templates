from __future__ import print_function

import numpy as np
import pandas as pd
from collections import OrderedDict
from datetime import datetime as dt

import orca
from urbansim.models import util

from ..__init__ import __version__


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
            out_column=None, out_transform=None, out_filters=None, name=None, tags=[]):
        
        self.tables = tables
        self.model_expression = model_expression
        self.filters = filters
        
        # TO DO - out_transform might not belong here - is it only used for OLS?
        
        self.out_tables = out_tables
        self.out_column = out_column
        self.out_transform = out_transform
        self.out_filters = out_filters
        
        self.name = name
        self.tags = tags
		
        
        self.template = type(self).__name__  # class name
        self.template_version = __version__
                

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
        # Pass values from the dictionary to the __init__() method
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
            'template': self.template,
            'template_version': self.template_version,
            'name': self.name,
            'tags': self.tags,
            'tables': self.tables,
            'model_expression': self.model_expression,
            'filters': self.filters,
            'out_tables': self.out_tables,
            'out_column': self.out_column,
            'out_transform': self.out_transform,
            'out_filters': self.out_filters,
        }
        return d
    
    
    def _normalize_table_param(self, tables):
        """
        Normalize table parameter input. TO DO - add more type validation
        
        """
        if isinstance(tables, list):
            # Normalize [] to None
            if len(tables) == 0:
                return None
        
            # Normalize [str] to str
            if len(tables) == 1:
                return tables[0]
                
        return tables
    
    
    @property
    def tables(self):
        return self.__tables
        
    @tables.setter
    def tables(self, tables):
        self.__tables = self._normalize_table_param(tables)
            
    @property
    def out_tables(self):
        return self.__out_tables
        
    @out_tables.setter
    def out_tables(self, out_tables):
        self.__out_tables = self._normalize_table_param(out_tables)


    def _get_df(self, tables='unset', fallback_tables=None, filters='unset',
            model_expression=None):
        """
        Generate a data table for estimation or prediction, relying on functionality from
        Orca and `urbansim.models.util`. This should be performed immediately before
        estimation or prediction so that it reflects the current data state.
        
        The output includes only the necessary columns: those mentioned in the model 
        expression or filters, plus (it appears) the index of each merged table. Relevant
        row filters are also applied.
        
        TO DO - this method is a generalization of _get_data(), and should replace it, 
        but does not currently support column filtering or PyLogit model expressions.
        
        Parameters
        ----------
        tables : str or list of str, optional
            Name of table or tables. If not provided, `self.tables` will be used.
        
        fallback_tables : str or list of str, optional
            Table(s) to use if first argument evaluates to `None`.
            
        filters : str or list of str, optional
            Filter(s) to apply. If not provided, `self.filters` will be used.
            
        model_expression : NOT YET IMPLEMENTED
            Model expression, for determining which columns are needed. If not provided,
            `self.model_expression` will be used.
            
            TO DO - this needs to handle the large MNL case where there are two sets of
            data tables, so we can't use urbansim.models.util.columns_in_formula()
        
        Returns
        -------
        DataFrame
        
        """
        if tables == 'unset':
            tables = self.tables
        
        if tables is None:
            tables = fallback_tables
            
        if filters == 'unset':
            filters = self.filters
        
        if isinstance(tables, list):
            df = orca.merge_tables(target=tables[0], tables=tables)
        else:
            df = orca.get_table(tables).to_frame()
        
        df = util.apply_filter_query(df, filters)
        return df
        
    
    def _get_data(self, task='fit'):
        """
        DEPRECATED - this should be replaced by the more general _get_df()
        
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
        # TO DO - verify input data
        
        if isinstance(self.model_expression, str):
            expr_cols = util.columns_in_formula(self.model_expression)
        
        # This is for PyLogit model expressions
        elif isinstance(self.model_expression, OrderedDict):
            # TO DO - check that this works in Python 2.7
            expr_cols = [t[0] for t in list(self.model_expression.items()) \
                         if t[0] is not 'intercept']
            # TO DO - not very general, maybe we should just override the method
            # TO DO - and this only applies to the fit condition
            if self.choice_column is not None:
                expr_cols += [self.choice_column]
        
        if (task == 'fit'):
            tables = self.tables
            columns = expr_cols + util.columns_in_filters(self.filters)
            filters = self.filters
        
        elif (task == 'predict'):
            if self.out_tables is not None:
                tables = self.out_tables
            else:
                tables = self.tables
                
            columns = expr_cols + util.columns_in_filters(self.out_filters)
            if self.out_column is not None:
                columns += [self.out_column]
            
            filters = self.out_filters
        
        if isinstance(tables, list):
            df = orca.merge_tables(target=tables[0], tables=tables, columns=columns)
        else:
            df = orca.get_table(tables).to_frame(columns)
            
        df = util.apply_filter_query(df, filters)
        return df


    def _get_filter_columns(self):
        """
        THIS METHOD DOES NOT WORK YET.   
        
        Return list of column names referenced in the filters.
        
        """
        return
    
    
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
			
    def _get_input_columns(self):
	
        """
        Return name of the column to save data to. This is rhs columns if it exsits,
         
        Returns
        -------
        list
        
        """
        rhs = self.model_expression.split('~')[1].strip().split('+')
        return [col.strip() for col in rhs]
    
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
        THIS METHOD IS DEPRECATED, AND SHOULD BE REPLACED BY UTILS.UPDATE_NAME().
        
        Generate a name for the class instance, based on its type and the current 
        timestamp. But if a custom name has already been provided, return that instead. 
        
        (We can't tell with certainty whether an existing name was auto-generated or
        customized, and it doesn't seem worth keeping track. A name is judged to be custom
        if it does not contain the class type.)
                
        Returns
        -------
        str
        
        """
        if (self.name is None) or (self.template in self.name):
            return self.template + '-' + dt.now().strftime('%Y%m%d-%H%M%S')
        else:
            return self.name
	
    def _split(self, n_splits=10):
		
        """
        take a data and turn it into a k-fold splits,where k=n_splits
        One split is reserved for testing, the rest will be used for training
        """
		
        data = self._get_data()
        data_index = np.array(data.index).astype('int64')
		
        np.random.shuffle(data_index)
        n_samples = data_index.shape[0]
		
        fold_sizes = (n_samples // n_splits) * np.ones(n_splits, dtype=np.int)
        fold_sizes[:n_samples % n_splits] += 1
        current = 0
        
        for fold_size in fold_sizes:
            start, stop = current, current + fold_size
            test_indices = data_index[start:stop]
            test_data = data.loc[test_indices]
            training_data = data.drop(test_indices)
            current = stop
            yield training_data, test_data
			
    def cross_validate_score(self, n_splits=10):
		
        data = self._get_data()
	
        output_column = self._get_out_column()
        self.rhs  = self._get_input_columns()
		
        self.cv_metric = {}
        i = 0
        
        mean_metric = np.zeros(n_splits)
        mae_metric = np.zeros(n_splits)
		
        for train, test in self._split(n_splits):
			
            y_train = np.array(train[output_column])
            X_train = np.array(train[self.rhs])
            self.model.fit(X_train, np.ravel(y_train))
            predicted = self.model.predict(test[self.rhs])
			
            mean_metric[i] = np.mean((predicted - test[output_column]) ** 2)
            mae_metric[i] = np.mean(abs(predicted - test[output_column]))
            i += 1
		
        self.cv_metric['mean_cross_validation'] = float(np.mean(mean_metric))
        self.cv_metric['mae_cross_validation'] = float(np.mean(mae_metric.mean()))
