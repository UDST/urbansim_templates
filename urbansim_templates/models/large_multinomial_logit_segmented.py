from __future__ import print_function

import numpy as np
import pandas as pd

import orca

from .. import modelmanager
from . import LargeMultinomialLogitStep


class MyData():
    def __init__(self):
        self._listeners = []
        self.a = 0
    
    @property
    def a(self):
        return self.__a
        
    @a.setter
    def a(self, value):
        self.__a = value
        self.send_to_listeners('a', value)
        
    def bind_to(self, callback):
        self._listeners.append(callback)
    
    def send_to_listeners(self, param, value):
        for callback in self._listeners:
            callback(param, value)
    
    def __repr__(self):
        return str(self.a)
        

@modelmanager.template
class SegmentedLargeMultinomialLogitStep():
    """
    
    If you set a property of the "default" model, it is immediately passed down to the 
    submodels. 
    
    
    Challenges
    - how to dynamically pass parameters from the defaults to the individual models,
      while maintaining the ability to NOT use defaults as well?
    
    Parameters
    ----------
    defaults : LargeMultinomialLogitStep, optional
    
    segmentation_column : str, optional
    
    name : str, optional
    
    tags : list of str, optional
    
    """
    def __init__(self, defaults=None, segmentation_column=None, name=None, tags=[]):
        
        self.defaults = MyData()
        self.defaults.bind_to(self.update_submodels)
        
        self.submodels = [MyData(), MyData()]
    
    
    def update_submodels(self, param, value):
        for m in self.submodels:
            m.a = value
    
    @property
    def defaults(self):
        return self.__defaults
    
    
    @defaults.setter
    def defaults(self, value):
        self.__defaults = value
    
    
    @classmethod
    def from_dict(cls, d):
        pass
    
    
    def to_dict(self):
        pass
    
    
    def build_submodels(self):
        """
        
        
        Expected class parameters
        -------------------------
        segmentation_column
        
        """
        
    
    def fit_all(self):
        """
        
        Parameters
        ----------
        update_with_default_params : bool, optional
            If True, runs `update_submodels()` before fitting.
        
        """
        if (len(self.submodels) == 0):
            self.build_submodels()
        
        pass
    
    
    def run(self):
        """
        Convenience method that invokes `run_all()`.
        
        """
        self.run_all()
    
    
    def run_all(self):
        """
        Not yet implemented.
        
        """
        pass