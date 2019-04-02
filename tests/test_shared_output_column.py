from __future__ import print_function

import pytest

from urbansim_templates.shared import CoreTemplateSettings


def test_property_persistence():
    """
    Confirm properties persist through to_dict() and from_dict().
    
    """
    obj = CoreTemplateSettings()
    obj.column_name = 'column'
    obj.table = 'table'
    obj.data_type = 'int32'
    obj.missing_values = 5
    obj.cache = True
    obj.cache_scope = 'iteration'
    
    d = obj.to_dict()
    print(d)
    
    obj2 = CoreTemplateSettings.from_dict(d)
    assert(obj2.to_dict() == d)

