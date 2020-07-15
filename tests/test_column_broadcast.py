import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import ColumnFromBroadcast
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca and ModelManager session, with data tables.
    
    """
    orca.clear_all()
    modelmanager.initialize()

    d = {'building_id': [1,2,3,4], 'value': [4,4,4,4]}
    df = pd.DataFrame(d).set_index('building_id')
    orca.add_table('buildings', df)

    d = {'household_id': [1,2,3], 'building_id': [2,3,4]}
    df = pd.DataFrame(d).set_index('household_id')
    orca.add_table('households', df)



###############################
## BEHAVIOR OF TEMPLATE











# def test_expression(orca_session):
#     """
#     Check that column is created and expression evaluated correctly.
#     
#     """
#     c = ColumnFromExpression()
#     c.column_name = 'c'
#     c.table = 'obs'
#     c.expression = 'a * 5 + sqrt(b)'
#     
#     c.run()
#     
#     val1 = orca.get_table('obs').get_column('c')
#     df = orca.get_table('obs').to_frame()
#     val2 = df.a * 5 + np.sqrt(df.b)
#     assert(val1.equals(val2))
#     
# 
# def test_data_type(orca_session):
#     """
#     Check that casting data type works.
#     
#     """
#     orca.add_table('tab', pd.DataFrame({'a': [0.1, 1.33, 2.4]}))
#     
#     c = ColumnFromExpression()
#     c.column_name = 'b'
#     c.table = 'tab'
#     c.expression = 'a'
#     c.run()
#     
#     v1 = orca.get_table('tab').get_column('b').values
#     np.testing.assert_equal(v1, [0.1, 1.33, 2.4])
#     
#     c.data_type = 'int'
#     c.run()
# 
#     v1 = orca.get_table('tab').get_column('b').values
#     np.testing.assert_equal(v1, [0, 1, 2])
# 
# 
# def test_missing_values(orca_session):
#     """
#     Check that filling in missing values works.
#     
#     """
#     orca.add_table('tab', pd.DataFrame({'a': [0.1, np.nan, 2.4]}))
#     
#     c = ColumnFromExpression()
#     c.column_name = 'b'
#     c.table = 'tab'
#     c.expression = 'a'
#     c.run()
#     
#     v1 = orca.get_table('tab').get_column('b').values
#     np.testing.assert_equal(v1, [0.1, np.nan, 2.4])
#     
#     c.missing_values = 5
#     c.run()
# 
#     v1 = orca.get_table('tab').get_column('b').values
#     np.testing.assert_equal(v1, [0.1, 5.0, 2.4])
# 
# 
# def test_modelmanager_registration(orca_session):
#     """
#     Check that modelmanager registration and auto-run work as expected.
#     
#     """
#     c = ColumnFromExpression()
#     c.column_name = 'c'
#     c.table = 'obs'
#     c.expression = 'a + b'
#     
#     modelmanager.register(c)
#     modelmanager.remove_step(c.name)
#     assert('c' in orca.get_table('obs').columns)
# 
# 
# def test_expression_with_standalone_columns(orca_session):
#     """
#     Check that expression can assemble data from stand-alone columns that are not part 
#     of the core DataFrame wrapped by a table.
#     
#     """
#     c = ColumnFromExpression()
#     c.column_name = 'c'
#     c.table = 'obs'
#     c.expression = 'a + b'
#     
#     modelmanager.register(c)
#     modelmanager.remove_step(c.name)
# 
#     d = ColumnFromExpression()
#     d.column_name = 'd'
#     d.table = 'obs'
#     d.expression = 'a + c'
#     
#     d.run()
#     assert('d' in orca.get_table('obs').columns)
# 




###############################
## SPEC CONFORMANCE AND BAD DATA INPUTS

def test_template_validity():
    """
    Check template conforms to basic spec.
    
    """
    assert validate_template(ColumnFromBroadcast)


# def test_missing_colname(orca_session):
#     """
#     Missing column_name should raise a ValueError.
#     
#     """
#     c = ColumnFromExpression()
#     c.table = 'tab'
#     c.expression = 'a'
#     
#     try:
#         c.run()
#     except ValueError as e:
#         print(e)
#         return
#     
#     pytest.fail()
# 
# 
# def test_missing_table(orca_session):
#     """
#     Missing table should raise a ValueError.
#     
#     """
#     c = ColumnFromExpression()
#     c.column_name = 'col'
#     c.expression = 'a'
#     
#     try:
#         c.run()
#     except ValueError as e:
#         print(e)
#         return
#     
#     pytest.fail()
# 
# 
# def test_missing_expression(orca_session):
#     """
#     Missing expression should raise a ValueError.
#     
#     """
#     c = ColumnFromExpression()
#     c.column_name = 'col'
#     c.table = 'tab'
#     
#     try:
#         c.run()
#     except ValueError as e:
#         print(e)
#         return
#     
#     pytest.fail()
# 
# 
