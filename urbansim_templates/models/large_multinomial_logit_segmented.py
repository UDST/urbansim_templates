from __future__ import print_function

import numpy as np
import pandas as pd

import orca

from .. import modelmanager
from . import LargeMultinomialLogitStep


class LargeMultinomialLogitDefaults(LargeMultinomialLogitStep):
    """
    This class extends LargeMultinomialLogitStep to 
    
    """
    def __init__(self, *args, **kwargs):
        self._listeners = []
        LargeMultinomialLogitStep.__init__(self, *args, **kwargs)
    
    def bind_to(self, callback):
        self._listeners.append(callback)
    
    def send_to_listeners(self, param, value):
        for callback in self._listeners:
            callback(param, value)
    
    @property
    def model_expression(self):
        return super(LargeMultinomialLogitStep, self).model_expression
        
    @model_expression.setter
    def model_expression(self, value):
        super(LargeMultinomialLogitStep, self.__class__).model_expression.fset(self, value)
        self.send_to_listeners('model_expression', value)
        
        

@modelmanager.template
class SegmentedLargeMultinomialLogitStep():
    """
    
    If you set a property of the "default" model, it is immediately passed down to the 
    submodels. 
    
    
    
    Parameters
    ----------
    defaults : LargeMultinomialLogitStep, optional
    
    segmentation_column : str, optional
    
    name : str, optional
    
    tags : list of str, optional
    
    """
    def __init__(self, defaults=None, segmentation_column=None, name=None, tags=[]):
        
        if defaults is None:
            defaults = LargeMultinomialLogitStep()
        
        self.defaults = defaults
        self.defaults.bind_to(self.update_submodels)
        
        self.submodels = [LargeMultinomialLogitStep(), LargeMultinomialLogitStep()]
    
    
    def update_submodels(self, param, value):
        """
        Updates a property across all the submodels. This function is bound to the 
        `defaults` object and runs automatically when one of its properties is changed.
        
        """
        for m in self.submodels:
            setattr(m, param, value)
    
    
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