from __future__ import print_function

import orca
from urbansim.utils import yamlio

from .models import OLSRegressionStep
from .models import BinaryLogitStep
from .models import MNLDiscreteChoiceStep


_STEPS = {}  # master repository of steps
_STARTUP_QUEUE = {}  # steps waiting to be registered

DISK_STORE = 'configs/modelmanager_configs.yaml'


def main():
    """
    Load steps from disk when the script is first imported.
    
    """
    # TO DO: is there a better way to handle this?
    if (len(_STEPS) == 0):
        load_steps_from_disk()
    

def list_steps():
    """
    Return a list of registered steps, with name, type, and tags for each.
    
    Returns
    -------
    list of dicts
    
    """
    # TO DO: does this dictionary iteration work in Python 2?

    l = [{'name': d['name'],
          'type': d['type'],
          'tags': d['tags']} for d in list(_STEPS.values())]
    
    return l


def add_step(d):
    """
    Register a model step from a dictionary representation conforming to UrbanSim 
    YAML spec v0.2. This will override any previously registered step with the same 
    name. The step will be registered with Orca and written to persistent storage.
    
    Parameters
    ----------
    d : dict
    
    """
    # TO DO - A long-term architecture issue here is that in order to create a class
    # object, we need to have already loaded the template definition. This is no problem
    # as long as all the templates are defined within `urbansim_templates`, because we can 
    # import them manually. But how should we handle it when we have arbitrary templates 
    # defined elsewhere? One approach would be to include the template location as an 
    # attribute in the yaml, and then import the necessary classes using `eval()`. But 
    # this opens us up to arbitrary code execution, which may not be very safe for a web 
    # service. Another approach would be to require users to import all the templates
    # they'll be using, before importing `modelmanager`. Then we can look them up using
    # `globals()[class_name]`. Safer, but less convenient. Must be other solutions too.
    
    if (d['name'] in _STEPS):
        remove_step(d['name'])
    
    _STEPS[d['name']] = d
    
    if (len(_STARTUP_QUEUE) == 0):
        save_steps_to_disk()

    # Create a callable that builds and runs the model step
    def run_step():
        return globals()[d['type']].from_dict(d).run()
        
    # Register it with Orca
    orca.add_step(d['name'], run_step)
        
    
def remove_step(name):
    """
    Remove a model step, by name. It will immediately be removed from ModelManager and 
    from persistent storage, but will remain registered in Orca until the current 
    Python process terminates.
    
    Parameters
    ----------
    name : str
    
    """
    del _STEPS[name]
    
    # TO DO: the re-saving isn't working when the list of model steps is empty

    if (len(_STARTUP_QUEUE) == 0):
        save_steps_to_disk()
    

def get_step(name):
    """
    Return the class representation of a registered step, by name.
    
    Parameters
    ----------
    name : str
    
    Returns
    -------
    RegressionStep or other
    
    """
    return globals()[_STEPS[name]['type']].from_dict(_STEPS[name])


def save_steps_to_disk():
    """
    Save current representation of model steps to disk, over-writing the previous file.
    
    """
    yamlio.convert_to_yaml(_STEPS, DISK_STORE)
    
    
def load_steps_from_disk():
    """
    Load all model steps from disk and register them with Orca.
    
    """
    # I'm doing this using a queue so that we can wait until all the pending registrations
    # are finished before saving back to disk. Is there a better approach?
    
    _STARTUP_QUEUE = yamlio.yaml_to_dict(str_or_buffer=DISK_STORE)
    
    while (len(_STARTUP_QUEUE) > 0):
        key, value = _STARTUP_QUEUE.popitem()
        add_step(value)
    

main()
