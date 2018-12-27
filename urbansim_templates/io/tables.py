from __future__ import print_function

import orca

from urbansim_templates import modelmanager


@modelmanager.template
class Table():
    """
    Class for registering data tables. In the initial implementation, data is expected to 
    be found locally in a CSV or HDF5 file.
    
    Parameters
    ----------
    
    name : str, optional
        Name of the table, for Orca. This will also be used as the name of the model step 
        that generates the table. 
    
    tags : list of str, optional
        Tags, passed to ModelManager.
    
    autorun : bool, optional
        Automatically "run" the step with the parameters passed to the constructor. This 
        will be set to True in dict representations of the object, so that loading it 
        into ModelManager will automatically register the table with Orca. 
    
    Properties and attributes
    -------------------------
    All the parameters listed above can also be get and set as properties of the class 
    instance.
    
    """
    def __init__(self):
        pass
    
    
    @classmethod
    def from_dict(cls, d):
        pass
    
    def to_dict(self):
        pass
    
    
    def validate(self):
        pass
    
    
    def run(self):
        pass