from __future__ import print_function

import numpy as np
import pandas as pd

import orca

from .. import modelmanager
from . import LargeMultinomialLogitStep


@modelmanager.template
class SegmentedLargeMultinomialLogitStep():
    """
    Questions
    - would you prefer submodels to be a dict indexed by the segmentation value, rather
      than a list as currently?
    
    Generating submodels: The first time you run "build_submodels()" or "fit_all()",
    submodels will be generated based on the `segmentation_column` and the current
    properties of the `defaults` object.
    
    Accessing submodels: 
    - After they're generated, you can access the individual submodel objects through the 
      `submodels` property (list of LargeMultinomialLogitSteps).
    
    Editing a submodel: 
    - Feel free to modify individual submodels as desired, except for the limitations 
      described below.
    
    Editing all submodels: 
    - Changing a property of the `defaults` object will update that property for all of 
      the submodels, without affecting other customizations.
    
    Limitations: 
    - The submodels are implemented by applying filters to the choosers table. If a prior 
      filter exists, the submodel filters will be added to it. The `chooser_filters` and 
      `out_chooser_filters` cannot be changed after submodels are generated. 
        
    
    Parameters
    ----------
    defaults : LargeMultinomialLogitStep, optional
    
    segmentation_column : str, optional
        Name of column in the choosers table.
    
    name : str, optional
    
    tags : list of str, optional
    
    """
    def __init__(self, defaults=None, segmentation_column=None, name=None, tags=[]):
        
        if defaults is None:
            defaults = LargeMultinomialLogitStep()
        
        self.defaults = defaults
        self.defaults.bind_to(self.update_submodels)
        
        self.submodels = [LargeMultinomialLogitStep(), LargeMultinomialLogitStep()]
    
    
    @classmethod
    def from_dict(cls, d):
        """
        Create an object instance from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        SegmentedLargeMultinomialLogitStep
        
        """
        # TO DO - implement
        pass
    
    
    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Returns
        -------
        dict
        
        """
        d = {
            'template': self.template,
            'template_version': self.template_version,
            'name': self.name,
            'tags': self.tags,
            'defaults': self.defaults.to_dict(),
            'submodels': [m.to_dict() for m in self.submodels]
        }
        return d
    
    
    def build_submodels(self):
        """
        Create a submodel for each category of choosers indicated by the segmentation
        column. (This column should contain categorical values.)
        
        Running this method will overwrite any previous submodels. It can be run as many
        times as desired.
        
        """
        # TO DO - implement
        self.submodels = []
        
    
    def update_submodels(self, param, value):
        """
        Updates a property across all the submodels. This method is bound to the 
        `defaults` object and runs automatically when one of its properties is changed.
        
        Parameters
        ----------
        param : str
            Property name.
        value : anything
        
        """
        for m in self.submodels:
            setattr(m, param, value)
    
    
    def fit_all(self):
        """
        Fit all the submodels. This method can be run as many times as desired.
        
        """
        if (len(self.submodels) == 0):
            self.build_submodels()
        
        for m in self.submodels:
            m.fit()
    
    
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