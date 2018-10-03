from __future__ import print_function
import numpy as np
import pandas as pd
from patsy import dmatrices

def version_parse(v):
    """
    Parses a version string into its component parts. String is expected to follow the 
    pattern "0.1.1.dev0", which would be parsed into (0, 1, 1, 0). The first two 
    components are required. The third is set to 0 if missing, and the fourth to None.
    
    Parameters
    ----------
    v : str
        Version string using syntax described above.
    
    Returns
    -------
    tuple with format (int, int, int, int or None)
    
    """
    v4 = None
    if 'dev' in v:
        v4 = int(v.split('dev')[1])
        v = v.split('dev')[0]  # 0.1.dev0 -> 0.1.
        
        if (v[-1] == '.'):
            v = v[:-1]  # 0.1. -> 0.1
        
    v = v.split('.')
    
    v3 = 0
    if (len(v) == 3):
        v3 = int(v[2])
    
    v2 = int(v[1])
    v1 = int(v[0])
    
    return (v1, v2, v3, v4)
    


def version_greater_or_equal(a, b):
    """
    Tests whether version string 'a' is greater than or equal to version string 'b'.
    Version syntax should follow the pattern described for `version_parse()`. 
    
    Note that 'dev' versions are pre-releases, so '0.2' < '0.2.1.dev5' < '0.2.1'.
        
    Parameters
    ----------
    a : str
        First version string, formatted as described in `version_parse()`. 
    b : str
        Second version string, formatted as described in `version_parse()`. 
    
    Returns
    -------
    boolean
    
    """
    a = version_parse(a)
    b = version_parse(b)
    
    if (a[0] > b[0]):
        return True
    
    elif (a[0] == b[0]):
        if (a[1] > b[1]):
            return True
            
        elif (a[1] == b[1]):
            if (a[2] > b[2]):
                return True
            
            elif (a[2] == b[2]):
                if (a[3] == None):
                    return True
                
                elif (b[3] == None):
                    return False
                
                elif (a[3] >= b[3]):
                    return True
    
    return False

def eval_rhs_function(model_expression, data):

	""""
	eval the functin, if any, from the strings in rhs (e.g 
	'np.log(variable)' will do: data[variable].apply(np.log)
	
	This is convenient utility to register transformation
	as part of the model
	
	The issue is arbitrary code execution, so we need to restrain
	the functions allowed. Right now use only functions implemented in
	numpy via patsy
	"""
	matrix_variables = dmatrices(model_expression + ' - 1', data, return_type='dataframe')
	df_x = pd.DataFrame(matrix_variables[1], index=data.index)
	df_y = pd.DataFrame(matrix_variables[0], index=data.index)
	
	return df_x, df_y
	

    	
	
def convert_to_model(model, model_expression, ytransform=None):

	""""
	This function takes a model with a predict and a fit attribute and 
	convert those attributes into a format compatible with .fit and .predict
	used by urbansim models
	"""
	model.fit_previous = model.fit
	model.predict_previous = model.predict
	
	def fit(data):
	
		# transform data using patsy dmatrix
		df_x, df_y = eval_rhs_function(model_expression, data)
	
		trainX = df_x
		trainY = np.ravel(np.array(df_y))
		
		return model.fit_previous(trainX, trainY)
		
	def predict(data):
	
		# transform data using patsy dmatrix
		df_x, _ = eval_rhs_function(model_expression, data)
		
		testX = np.array(df_x)
		values = model.predict_previous(testX)
		
		if ytransform:
			values = ytransform(values)
		return pd.Series(pd.Series(values, index=data.index))
	
	model.fit = fit
	model.predict = predict
	return model 
		
    
    