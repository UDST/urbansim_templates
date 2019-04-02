import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import ColumnFromExpression
from urbansim_templates.utils import validate_template


@pytest.fixture
def orca_session():
    """
    Set up a clean Orca and ModelManager session, with a data table.
    
    """
    orca.clear_all()
    modelmanager.initialize()

    d1 = {'id': np.arange(5), 
          'a': np.random.random(5),
          'b': np.random.choice(np.arange(20), size=5)}

    df = pd.DataFrame(d1).set_index('id')
    orca.add_table('obs', df)


# def test_template_validity():
#     """
#     Check template conforms to basic spec.
#     
#     """
#     assert validate_template(ColumnFromExpression)


def test_missing_colname(orca_session):
    """
    Missing column_name should raise a ValueError.
    
    """
    c = ColumnFromExpression()
    c.table = 'tab'
    c.expression = 'a'
    
    try:
        c.run()
    except ValueError as e:
        print(e)
        return
    
    pytest.fail()


def test_missing_table(orca_session):
    """
    Missing table should raise a ValueError.
    
    """
    c = ColumnFromExpression()
    c.output.column_name = 'col'
    c.expression = 'a'
    
    try:
        c.run()
    except ValueError as e:
        print(e)
        return
    
    pytest.fail()


def test_missing_expression(orca_session):
    """
    Missing expression should raise a ValueError.
    
    """
    c = ColumnFromExpression()
    c.output.column_name = 'col'
    c.table = 'tab'
    
    try:
        c.run()
    except ValueError as e:
        print(e)
        return
    
    pytest.fail()


def test_expression(orca_session):
    """
    Check that column is created and expression evaluated correctly.
    
    """
    c = ColumnFromExpression()
    c.output.column_name = 'c'
    c.table = 'obs'
    c.expression = 'a * 5 + sqrt(b)'
    
    c.run()
    
    val1 = orca.get_table('obs').get_column('c')
    df = orca.get_table('obs').to_frame()
    val2 = df.a * 5 + np.sqrt(df.b)
    assert(val1.equals(val2))
    

def test_data_type(orca_session):
    """
    Check that casting data type works.
    
    """
    orca.add_table('tab', pd.DataFrame({'a': [0.1, 1.33, 2.4]}))
    
    c = ColumnFromExpression()
    c.output.column_name = 'b'
    c.table = 'tab'
    c.expression = 'a'
    c.run()
    
    v1 = orca.get_table('tab').get_column('b').values
    np.testing.assert_equal(v1, [0.1, 1.33, 2.4])
    
    c.output.data_type = 'int'
    c.run()

    v1 = orca.get_table('tab').get_column('b').values
    np.testing.assert_equal(v1, [0, 1, 2])


def test_missing_values(orca_session):
    """
    Check that filling in missing values works.
    
    """
    orca.add_table('tab', pd.DataFrame({'a': [0.1, np.nan, 2.4]}))
    
    c = ColumnFromExpression()
    c.output.column_name = 'b'
    c.table = 'tab'
    c.expression = 'a'
    c.run()
    
    v1 = orca.get_table('tab').get_column('b').values
    np.testing.assert_equal(v1, [0.1, np.nan, 2.4])
    
    c.output.missing_values = 5
    c.run()

    v1 = orca.get_table('tab').get_column('b').values
    np.testing.assert_equal(v1, [0.1, 5.0, 2.4])


def test_modelmanager_registration(orca_session):
    """
    Check that modelmanager registration and auto-run work as expected.
    
    """
    c = ColumnFromExpression()
    c.output.column_name = 'c'
    c.table = 'obs'
    c.expression = 'a + b'
    
    modelmanager.register(c)
    modelmanager.remove_step(c.meta.name)
    assert('c' in orca.get_table('obs').columns)


def test_expression_with_standalone_columns(orca_session):
    """
    Check that expression can assemble data from stand-alone columns that are not part 
    of the core DataFrame wrapped by a table.
    
    """
    c = ColumnFromExpression()
    c.output.column_name = 'c'
    c.table = 'obs'
    c.expression = 'a + b'
    
    modelmanager.register(c)
    modelmanager.remove_step(c.meta.name)

    d = ColumnFromExpression()
    d.output.column_name = 'd'
    d.table = 'obs'
    d.expression = 'a + c'
    
    d.run()
    assert('d' in orca.get_table('obs').columns)

