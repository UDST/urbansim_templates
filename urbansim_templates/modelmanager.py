from __future__ import print_function

import os
import copy
import pickle
from collections import OrderedDict

import orca
from urbansim.utils import yamlio

from .__init__ import __version__
from .utils import update_name, version_greater_or_equal


_templates = {}  # global registry of template classes
_steps = {}  # global registry of model steps in memory
_disk_store = None  # path to saved steps on disk


def template(cls):
    """
    This is a decorator for ModelManager-compliant template classes. Place
    `@modelmanager.template` on the line before a class defintion.
    
    This makes the class available to ModelManager (e.g. for reading saved steps from 
    disk) whenever it's imported.
    
    """
    _templates[cls.__name__] = cls
    return cls
    

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
    Build a model step object from a saved dictionary. This includes loading supplemental
    objects from disk.
    
    Parameters
    ----------
    d : dict
        Representation of a model step.
    
    Returns
    -------
    object
    
    """
    if 'supplemental_objects' in d:
        for i, item in enumerate(d['supplemental_objects']):
            content = load_supplemental_object(d['name'], **item)
            d['supplemental_objects'][i]['content'] = content
    
    return _templates[d['template']].from_dict(d)
    

def load_supplemental_object(step_name, name, content_type, required=True):
    """
    Load a supplemental object from disk.
    
    Parameters
    ----------
    step_name : str
        Name of the associated model step.
    name : str
        Name of the supplemental object.
    content_type : str
        Currently supports 'pickle'.
    required : bool, optional
        Whether the supplemental object is required (not yet supported).
    
    Returns
    -------
    object
    
    """
    if (content_type == 'pickle'):
        with open(os.path.join(_disk_store, step_name+'-'+name+'.pkl'), 'rb') as f:
            return pickle.load(f)
    

def register(step, save_to_disk=True):
    """
    Register a model step with ModelManager and Orca. This includes saving it to disk,
    optionally, so it can be automatically loaded in the future.
    
    Registering a step will overwrite any previously loaded step with the same name. If a 
    name has not yet been assigned, one will be generated from the template name and a 
    timestamp.
    
    Parameters
    ----------
    step : object
    
    """
    if step.name is None:
        step.name = update_name(step.template, step.name)  # TO DO - test this
    
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
    
    d = step.to_dict()
    
    # Save supplemental objects
    if 'supplemental_objects' in d:
        for item in filter(None, d['supplemental_objects']):
            save_supplemental_object(step.name, **item)
            del item['content']
    
    # Save main yaml file
    headers = {'modelmanager_version': __version__}

    content = OrderedDict(headers)
    content.update({'saved_object': d})
    
    yamlio.convert_to_yaml(content, os.path.join(_disk_store, step.name+'.yaml'))
    

def save_supplemental_object(step_name, name, content, content_type, required=True):
    """
    Save a supplemental object to disk.
    
    Parameters
    ----------
    step_name : str
        Name of the associated model step.
    name : str
        Name of the supplemental object.
    content : obj
        Object to save.
    content_type : str
        Currently supports 'pickle'.
    required : bool, optional
        Whether the supplemental object is required (not yet supported).
    
    """
    if content_type == 'pickle':
        content.to_pickle(os.path.join(_disk_store, step_name+'-'+name+'.pkl'))
        

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
    return copy.deepcopy(_steps[name])


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
    
    d = _steps[name].to_dict()
    
    if 'supplemental_objects' in d:
        for item in filter(None, d['supplemental_objects']):
            remove_supplemental_object(name, item['name'], item['content_type'])

    del _steps[name]
    os.remove(os.path.join(_disk_store, name+'.yaml'))
    

def remove_supplemental_object(step_name, name, content_type):
    """
    Remove a supplemental object from disk.
    
    Parameters
    ----------
    step_name : str
        Name of the associated model step.
    name : str
        Name of the supplemental object.
    content_type : str
        Currently supports 'pickle'.
    
    """
    # TO DO - check that the file exists first
    
    if content_type == 'pickle':
        os.remove(os.path.join(_disk_store, step_name+'-'+name+'.pkl'))
    

def get_config_dir():
    """
    Return the config directory, for other services that need to interoperate.
    
    Returns
    -------
    str
    
    """
    return _disk_store

