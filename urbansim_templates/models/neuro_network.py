from __future__ import print_function

import numpy as np
import pandas as pd
from datetime import datetime as dt

import orca
from urbansim.utils import yamlio

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.wrappers.scikit_learn import KerasRegressor


from .. import modelmanager
from ..utils import convert_to_model
from .shared import TemplateStep

		
@modelmanager.template		
class NeuralNetworkStep(TemplateStep):

	def __init__(self, tables=None, model_expression=None, filters=None, out_tables=None,
            out_column=None, out_transform=None, out_filters=None, name=None, tags=[]):
		
		super().__init__(tables=tables, model_expression=model_expression, filters=filters, out_tables=out_tables,
            out_column=out_column, out_transform=out_transform, name=name)
		
		self.cv_metric = None
		self.importance = None
		
		

	@classmethod
	def from_dict(cls, d):
		"""
        Create an object instance from a saved dictionary representation.
        Use a pickled version of the random forest model
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        RandomForestRegressionStep
        
		"""	
		# Pass values from the dictionary to the __init__() method
		obj = cls(tables=d['tables'], model_expression=d['model_expression'], 
                filters=d['filters'], out_tables=d['out_tables'], 
                out_column=d['out_column'], out_transform=d['out_transform'],
                out_filters=d['out_filters'], name=d['name'], tags=d['tags'],
				)

		return obj

	def baseline_model(self):
		
		# create model
		model = Sequential()
		model.add(Dense(len(self.rhs), input_dim=len(self.rhs), 
						kernel_initializer='normal', 
						activation='relu'))
		model.add(Dense(len(self.rhs), input_dim=len(self.rhs), 
						kernel_initializer='normal', 
						activation='relu'))
		model.add(Dropout(0.05))
		model.add(Dense(1, kernel_initializer='normal'))
		
		# Compile model
		model.compile(loss='mean_squared_error', optimizer='adam')
		return model
	

	def fit(self, **keywords):
	
		
		self.rhs  = self._get_input_columns()
	
		# convert model to  a format -- similar fit and predict structure -- than other steps
		estimator = self.baseline_model()

		self.model = convert_to_model(estimator, 
									  self.model_expression, 
									  ytransform=self.out_transform)
	
		results = self.model.fit(self._get_data(), **keywords)
		
		self.name = self._generate_name()
		
	def to_dict(self):
		"""
        Create a dictionary representation of the object.
        
        Returns
        -------
        dict
        
		"""
		d = TemplateStep.to_dict(self)
		# Add parameters not in parent class
		d.update({
            'model': self.name,
			'cross validation metric': self.cv_metric,
			'features importance': self.importance
        })
		
		# model config is a filepath to a pickled file
		d['supplemental_objects'] = []
		d['supplemental_objects'].append({'name': self.name,
									'content': self.model, 
									'content_type': 'pickle'})
		
		return d
		
	def run(self):
		"""
		Run the model step: calculate predicted values and use them to update a column.
        
        The predicted values are written to Orca and also saved to the class object for 
        interactive use (`predicted_values`, with type pd.Series). But they are not saved 
        in the dictionary representation of the model step.
        
        """
		# TO DO - figure out what we can infer about requirements for the underlying data
        # and write an 'orca_test' assertion to confirm compliance.

		output_column = self._get_out_column()
		data = self._get_data('predict')
		
		values = self.model.predict(self._get_data('predict'))
		self.predicted_values = values
       
		tabname = self._get_out_table()

		orca.get_table(tabname).update_col_from_series(output_column, values, cast=True)
		
