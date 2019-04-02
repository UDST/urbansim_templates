from __future__ import print_function

import pytest

from urbansim_templates.shared import CoreTemplateSettings


def test_property_persistence():
    """
    Confirm properties persist through to_dict() and from_dict().
    
    """
    obj = CoreTemplateSettings()
    obj.name = 'name'
    obj.tags = ['tag1', 'tag2']
    obj.notes = 'notes'
    obj.autorun = True
    obj.template = 'CoolNewTemplate'
    obj.template_version = '0.1.dev0'
    
    d = obj.to_dict()
    print(d)
    
    obj2 = CoreTemplateSettings.from_dict(d)
    assert(obj2.to_dict() == d)

