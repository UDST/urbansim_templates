import orca
import numpy as np
import pandas as pd
import pytest

from urbansim_templates import modelmanager
from urbansim_templates.models.regression import GradientBoostingRegressionStep

# load rental data
rental = pd.read_csv('data\\rentals_with_nodes.csv')
node_small = pd.read_csv('data\\nodessmall_vars.csv') 
node_walk = pd.read_csv('data\\nodeswalk_vars.csv') 

data = pd.merge(rental, node_small, left_on='node_id_small', right_on='osmid')
data = pd.merge(data, node_walk, left_on='node_id_walk', right_on='osmid')

# add columns -- we need a way to register those transformations in the model
data['log_rent_sqft'] = np.log(data.rent_sqft)


# register data in orca
orca.add_table('rental_prices', data)

def test_gb():
    """
    For now this just tests that the code runs.
    
    """
    modelmanager.initialize()

	# gradient boosting
    bg = GradientBoostingRegressionStep(out_transform=np.exp, out_column='rent_sqft')
    bg.tables = 'rental_prices'
    bg.n_splits = 10
    bg.model_expression = 'np.log(rent_sqft) ~ bedrooms + np.log1p(units_500_walk) + np.log1p(rich_500_walk) + np.log1p(singles_500_walk)'
	
    bg.name = 'cross_validate_boosting_-test'
   
    bg.fit()
    bg.cross_validate_score()
    print(bg.cv_metric)
    modelmanager.register(bg)
    
    
	
if __name__ == '__main__':
    test_gb()
	