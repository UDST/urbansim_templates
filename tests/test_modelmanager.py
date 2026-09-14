import itertools
from datetime import datetime

import orca
import pytest

from urbansim_templates import modelmanager, utils
from urbansim_templates.data import ColumnFromExpression, LoadTable


@pytest.fixture
def orca_session():
    orca.clear_all()
    modelmanager.initialize()


@pytest.fixture
def ticking_clock(monkeypatch):
    """
    Make every call to the clock used for automatic step names return a later second,
    so that a name regenerated on reload would be visibly different.
    
    """
    seconds = itertools.count()
    
    class FakeDatetime(object):
        @staticmethod
        def now():
            return datetime(2026, 1, 1, 12, 0, next(seconds))
    
    monkeypatch.setattr(utils, 'dt', FakeDatetime)


def test_auto_name_generated_once(orca_session, ticking_clock):
    """
    A step without a name gets one on registration, and keeps it when re-registered.
    
    """
    t = LoadTable(table='buildings', source_type='csv', path='data/buildings.csv',
                  autorun=False)
    assert t.name is None
    
    modelmanager.register(t)
    name = t.name
    assert name == 'LoadTable-20260101-120000'
    
    modelmanager.register(t)
    assert t.name == name
    
    modelmanager.remove_step(name)


def test_auto_name_survives_reload(orca_session, ticking_clock):
    """
    Reloading steps from disk keeps their names, so they stay in sync with the YAML
    files and can be looked up and removed by the name reported at registration.
    
    """
    t = LoadTable(table='buildings', source_type='csv', path='data/buildings.csv',
                  autorun=False)
    modelmanager.register(t)
    name = t.name
    
    modelmanager.initialize()
    assert [s['name'] for s in modelmanager.list_steps()] == [name]
    assert modelmanager.get_step(name).name == name
    
    modelmanager.remove_step(name)
    assert modelmanager.list_steps() == []


def test_auto_name_with_meta_settings(orca_session, ticking_clock):
    """
    Same checks for a template that keeps its name in a settings object (step.meta).
    
    """
    c = ColumnFromExpression()
    c.meta.autorun = False
    c.data.table = 'obs'
    c.data.expression = 'a + b'
    c.output.column_name = 'c'
    assert c.meta.name is None
    
    modelmanager.register(c)
    name = c.meta.name
    assert name == 'ColumnFromExpression-20260101-120000'
    
    modelmanager.register(c)
    assert c.meta.name == name
    
    modelmanager.initialize()
    assert [s['name'] for s in modelmanager.list_steps()] == [name]
    assert modelmanager.get_step(name).meta.name == name
    
    modelmanager.remove_step(name)


def test_custom_name_kept(orca_session, ticking_clock):
    t = LoadTable(table='buildings', source_type='csv', path='data/buildings.csv',
                  autorun=False, name='buildings-loader')
    modelmanager.register(t)
    assert t.name == 'buildings-loader'
    
    modelmanager.initialize()
    assert [s['name'] for s in modelmanager.list_steps()] == ['buildings-loader']
    modelmanager.remove_step('buildings-loader')
