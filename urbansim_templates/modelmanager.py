from __future__ import print_function

import os
from collections import OrderedDict

import orca
from urbansim.utils import yamlio

from .models import OLSRegressionStep
from .models import BinaryLogitStep
from .models import LargeMultinomialLogitStep
from .models import SmallMultinomialLogitStep

from .__init__ import __version__
from .utils import version_greater_or_equal


_STEPS = {}  # master dictionary of steps in memory
_DISK_STORE = None  # path to saved steps on disk


def initialize(path='configs'):
    """
    Load saved model steps from disk. Each file in the directory will be checked for 
    compliance with the ModelManager YAML format and then loaded into memory.
    
    If run multiple times, steps will be cleared from memory and re-loaded.
    
    Parameters
    ----------
    path : str
        Path to config directory, either absolute or relative to the Python working 
        directory
    
    """
    if not os.path.exists(path):
        print("Path not found: {}".format(os.path.join(os.getcwd(), path)))
        # TO DO - automatically create directory if run again after warning?
        return
        
    global _STEPS, _DISK_STORE
    _STEPS = {}  # clear memory
    _DISK_STORE = path  # save initialization path
    
    files = []
    for f in os.listdir(path):
        if f[-5:] == '.yaml':
            files.append(os.path.join(path, f))
    
    if len(files) == 0:
        print("No yaml files found in path '{}'".format(path))
        return
        
    steps = []
    for f in files:
        d = yamlio.yaml_to_dict(str_or_buffer=f)
        if 'modelmanager_version' in d:
            # TO DO - check that file name matches object name in the file?
            if version_greater_or_equal(d['modelmanager_version'], '0.1.dev8'):
                # This is the version that switched from a single file to multiple files
                # with one object stored in each
                steps.append(d)            
    
    if len(steps) == 0:
        print("No files from ModelManager 0.1.dev8 or later found in path '{}'"\
                .format(path))
    
    for d in steps:
        # TO DO - check for this key, to be safe
        add_step(d['saved_object'], save_to_disk=False)    


def list_steps():
    """
    Return a list of registered steps, with name, type, and tags for each.
    
    Returns
    -------
    list of dicts, ordered by name
    
    """
    l = [{'name': _STEPS[k]['name'],
          'type': _STEPS[k]['type'],
          'tags': _STEPS[k]['tags']} for k in sorted(_STEPS.keys())]
    
    return l


def add_step(d, save_to_disk=True):
    """
    Register a model step from a dictionary representation. This will override any 
    previously registered step with the same name. The step will be registered with Orca 
    and (if save_to_disk==True) written to persistent storage.
    
    Note: This function is intended for internal use. In a model building workflow, it's 
    better to use an object's `register()` method to register it with ModelManager and 
    save it to disk at the same time.
    
    Parameters
    ----------
    d : dict
    save_to_disk : bool
    
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
    
    if save_to_disk:
        save_step(d)
    
    print("Loading model step '{}'".format(d['name']))
    
    _STEPS[d['name']] = d
    
    # Create a callable that builds and runs the model step
    def run_step():
        return globals()[d['type']].from_dict(d).run()
        
    # Register it with Orca
    orca.add_step(d['name'], run_step)
        
    
def save_step(d):
    """
    Save a model step to disk, over-writing the previous file. The file will be named
    'model-name.yaml' and will be saved to the initialization directory.
    
    Note: This function is for internal use. In a model building workflow, it's better to
    use an object's `register()` method to register it with ModelManager and save it to 
    disk at the same time.
    
    """
    if _DISK_STORE is None:
        print("Please run 'mm.initialize()' before registering new model steps")
        return
    
    print("Saving '{}.yaml': {}".format(d['name'], 
            os.path.join(os.getcwd(), _DISK_STORE)))
    
    headers = {'modelmanager_version': __version__}

    content = OrderedDict(headers)
    content.update({'saved_object': d})
    
    yamlio.convert_to_yaml(content, os.path.join(_DISK_STORE, d['name']+'.yaml'))
    

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
    return globals()[_STEPS[name]['template']].from_dict(_STEPS[name])    


def remove_step(name):
    """
    Remove a model step, by name. It will immediately be removed from ModelManager and 
    from disk, but will remain registered in Orca until the current Python process 
    terminates.
    
    Parameters
    ----------
    name : str
    
    """
    print("Removing '{}' and '{}.yaml'".format(name, name))

    del _STEPS[name]
    
    os.remove(os.path.join(_DISK_STORE, name+'.yaml'))
    

def get_config_dir():
    """
    Return the config directory, for other services that need to interoperate.
    
    Returns
    -------
    str
    
    """
    return _DISK_STORE

