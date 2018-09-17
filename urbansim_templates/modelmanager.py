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


_steps = {}  # master dictionary of steps in memory
_disk_store = None  # path to saved steps on disk


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
        
    global _steps, _disk_store
    _steps = {}  # clear memory
    _disk_store = path  # save initialization path
    
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
        step = build_step(d['saved_object'])
        register(step, save_to_disk=False)


def build_step(d):
    """
    Build a model step object from a dictionary representation. This includes loading
    non-dict content from disk.
    
    Parameters
    ----------
    d : dict
        Representation of a model step.
    
    """
    # TO DO - HANDLE NON-DICT CONTENT
    return globals()[d['template']].from_dict(d)
    

def register(step, save_to_disk=True):
    """
    Register a model step with ModelManager and Orca. This includes saving it to disk,
    optionally, so it can be automatically loaded in the future.
    
    Registering a step will overwrite any previously loaded step with the same name.
    
    Parameters
    ----------
    step : object
    
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
        save_step_to_disk(step)
    
    print("Registering model step '{}'".format(step.name))
    
    _steps[step.name] = step
    
    # Create a callable that runs the model step, and register it with orca
    def run_step():
        return step.run()
        
    orca.add_step(step.name, run_step)
        
    
def list_steps():
    """
    Return a list of registered steps, with name, template, and tags for each.
    
    Returns
    -------
    list of dicts, ordered by name
    
    """
    return [{'name': _steps[k].name,
             'template': type(_steps[k]).__name__,
             'tags': _steps[k].tags} for k in sorted(_steps.keys())]
    

def save_step_to_disk(step):
    """
    Save a model step to disk, over-writing the previous file. The file will be named
    'model-name.yaml' and will be saved to the initialization directory.
    
    """
    if _disk_store is None:
        print("Please run 'modelmanager.initialize()' before registering new model steps")
        return
    
    print("Saving '{}.yaml': {}".format(step.name, 
            os.path.join(os.getcwd(), _disk_store)))
    
    headers = {'modelmanager_version': __version__}

    content = OrderedDict(headers)
    content.update({'saved_object': step.to_dict()})
    
    yamlio.convert_to_yaml(content, os.path.join(_disk_store, step.name+'.yaml'))
    
    # TO DO - HANDLE NON-DICT CONTENT
    

def save_nondict_content(object, name, content_type, required=True):
    """
    Save additional content to disk beyond the dictionary representation of a model step.
    Currently, only pickled objects are supported.
    
    Parameters
    ----------
    object : obj
        Object to save.
    name : str
        Filename without extension.
    content_type : 'pickle'
        Content type.
    required : bool
        Indication of whether storing the item is required or optional.
    
    """
    if content_type is 'pickle':
        object.to_pickle(os.path.join(_disk_store, name+'.pkl'))
        

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
    return _steps[name]


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

    del _steps[name]
    
    os.remove(os.path.join(_disk_store, name+'.yaml'))
    
    # TO DO - ALSO REMOVE NON-DICT CONTENT
    

def get_config_dir():
    """
    Return the config directory, for other services that need to interoperate.
    
    Returns
    -------
    str
    
    """
    return _disk_store

