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
    """From a patsy string to the corresponding column in data
    
    This function looks at each variable names in a 
    patsy sting, evaluate potential numpy functions applied to that variable 
    and select the corresponding columns in data
    
    This is convenient utility to register transformation
    as part of the model
    
    Example
    --------
    >>> model_expression = 'np.log(y) ~ np.log1p(x)'
    >>> data = pd.DataFrame([[0, 0, 3], [0,2, 4]])
    >>> data.columns =['x', 'y', 'z']
    >>> eval_rhs_function(model_expression, data)
    
    Arguments
    --------
    model_expression: a patsy string 
            model formula "lhs' ~ 'rhs' with possibly numpy function applied to 
            rhs and/or lhs variables
    
    data: pandas dataframe
            dataframe with columns including all variable in model_expression
            
    Returns
    --------
    df_x: pandas dataframe
            a dataframe with transformed rhs variables
    
    df_y: pandas series
            a series with tranformed lhs variable
    
    To do
    -------
    The issue is arbitrary code execution, so we need to restrain
    the functions allowed. Right now use only functions implemented in
    numpy via patsy
    """
    matrix_variables = dmatrices(model_expression + ' - 1', data, return_type='dataframe')
    df_x = pd.DataFrame(matrix_variables[1], index=data.index)
    df_y = pd.DataFrame(matrix_variables[0], index=data.index)
    
    return df_x, df_y
    
  
def convert_to_model(model, model_expression, ytransform=None):
    """Convert model to the right format 
    
    This function returns a model with a fit and predict method compatible with the 
    TemplateStep structure.
    
    Example
    ----------
    >>> from sklearn.ensemble import RandomForestRegressor
    >>> model = RandomForestRegressor()
    >>> model_expression = 'np.log(y) ~ np.log1p(x)'
    >>> new_model = convert_to_model(model, model_expression)
    >>> trainX = np.array(data['X'])
    >>> trainY = np.array(data['Y']
    Compare new_model.fit(data) to model.fit(np.log1p(trainX), np.log(trainY))
    
    Arguments
    ---------
    model: object 
            model with a fit and predict method
    
    model_expression: a patsy string 
            model formula "lhs' ~ 'rhs' with possibly numpy function applied to 
            rhs and/or lhs variables
       
    Keywords:
    ---------
    ytransform: numpy function 
            applied to the output once predicted
    
    Returns
    ---------
    object
            model with modified fit and predict methods
    """
    
    model.fit_previous = model.fit
    model.predict_previous = model.predict
    
    def fit(data, **keywords):
    
        # transform data using patsy dmatrix
        df_x, df_y = eval_rhs_function(model_expression, data)
    
        trainX = df_x
        trainY = np.ravel(np.array(df_y))
        
        return model.fit_previous(trainX, trainY, **keywords)
        
    def predict(data):
    
        # transform data using patsy dmatrix
        df_x, _ = eval_rhs_function(model_expression, data)
        
        testX = np.array(df_x)
        values = model.predict_previous(testX).ravel()
    
        if ytransform:
            values = ytransform(values)
        
        return pd.Series(pd.Series(values, index=data.index))
    
    model.fit = fit
    model.predict = predict
    return model 
        
    
    
