import numpy as np
import pandas as pd
import pytest

import orca

from urbansim_templates import modelmanager
from urbansim_templates.data import ColumnFromExpression, ExpressionSettings
from urbansim_templates.utils import validate_template


def test_expression_settings_persistence():
    """
    Confirm ExpressionSettings properties persist through the constructor, to_dict(),
    and from_dict().
    
    """
    d = {'table': 'tab', 'expression': 'a + b + c'}
    obj = ExpressionSettings(table = 'tab', expression = 'a + b + c')

    assert(d == obj.to_dict() == ExpressionSettings.from_dict(d).to_dict())


def test_legacy_data_loader(orca_session):
    """
    Check that loading a saved dict with the legacy format works.
    
    """
    d = {
        'name': 'n',
        'tags': ['a', 'b'],
        'autorun': False,
        'column_name': 'col',
        'table': 'tab',
        'expression': 'abc',
        'data_type': 'int',
        'missing_values': 5,
        'cache': True,
        'cache_scope': 'step'}
    
    c = ColumnFromExpression.from_dict(d)
    assert(c.meta.name == d['name'])
    assert(c.meta.tags == d['tags'])
    assert(c.meta.autorun == d['autorun'])
    assert(c.data.table == d['table'])
    assert(c.data.expression == d['expression'])
    assert(c.output.column_name == d['column_name'])
    assert(c.output.data_type == d['data_type'])
    assert(c.output.missing_values == d['missing_values'])
    assert(c.output.cache == d['cache'])
    assert(c.output.cache_scope == d['cache_scope'])


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
    c.data.table = 'tab'
    c.data.expression = 'a'
    
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
    c.data.expression = 'a'
    c.output.column_name = 'col'
    
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
    c.data.table = 'tab'
    c.output.column_name = 'col'
    
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
    c.data.table = 'obs'
    c.data.expression = 'a * 5 + sqrt(b)'
    c.output.column_name = 'c'
    
    c.run()
    
    val1 = orca.get_table('obs').get_column('c')
    df = orca.get_table('obs').to_frame()
    val2 = df.a * 5 + np.sqrt(df.b)
    assert(val1.equals(val2))
    

def test_modelmanager_registration(orca_session):
    """
    Check that modelmanager registration and auto-run work as expected.
    
    """
    c = ColumnFromExpression()
    c.data.table = 'obs'
    c.data.expression = 'a + b'
    c.output.column_name = 'c'
    
    modelmanager.register(c)
    modelmanager.remove_step(c.meta.name)
    assert('c' in orca.get_table('obs').columns)


def test_expression_with_standalone_columns(orca_session):
    """
    Check that expression can assemble data from stand-alone columns that are not part 
    of the core DataFrame wrapped by a table.
    
    """
    c = ColumnFromExpression()
    c.data.table = 'obs'
    c.data.expression = 'a + b'
    c.output.column_name = 'c'
    
    modelmanager.register(c)
    modelmanager.remove_step(c.meta.name)

    d = ColumnFromExpression()
    d.data.table = 'obs'
    d.data.expression = 'a + c'
    d.output.column_name = 'd'
    
    d.run()
    assert('d' in orca.get_table('obs').columns)

