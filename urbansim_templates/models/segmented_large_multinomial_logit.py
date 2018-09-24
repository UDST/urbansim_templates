from __future__ import print_function

import copy

import numpy as np
import pandas as pd

import orca

from ..__init__ import __version__
from ..utils import update_name
from .. import modelmanager
from . import LargeMultinomialLogitStep


@modelmanager.template
class SegmentedLargeMultinomialLogitStep():
    """
    TO DO - finish documentation
    
    Generating submodels: 
    - The first time you run "build_submodels()" or "fit_all()", submodels will be 
      generated based on the `segmentation_column` and the current properties of the 
      `defaults` object.
    
    Accessing submodels: 
    - After they're generated, you can access the individual submodel objects through the 
      `submodels` property (list of LargeMultinomialLogitSteps).
    
    Editing a submodel: 
    - Feel free to modify individual submodels as desired.
    
    Editing all submodels: 
    - Changing a property of the `defaults` object will update that property for all of 
      the submodels, without affecting other customizations.
    
    Limitations: 
    - The submodels are implemented by applying filters to the choosers table. If a prior 
      filter exists, the submodel filters will be added to it.
        
    
    Parameters
    ----------
    defaults : LargeMultinomialLogitStep, optional
    
    segmentation_column : str, optional
        Name of a column containing categorical data. Should be found in the `choosers`
        table of the `defaults` object.
    
    name : str, optional
    
    tags : list of str, optional
    
    """
    def __init__(self, defaults=None, segmentation_column=None, name=None, tags=[]):
        
        if defaults is None:
            defaults = LargeMultinomialLogitStep()
        
        self.defaults = defaults
        self.defaults.bind_to(self.update_submodels)
        
        self.submodels = {}
    
        self.name = name
        self.tags = tags
        
        self.template = type(self).__name__  # class name
        self.template_version = __version__

    
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
        mnl_step = LargeMultinomialLogitStep.from_dict
        
        obj = cls(
            defaults = mnl_step(d['defaults']),
            segmentation_column = d['segmentation_column'],
            name = d['name'],
            tags = d['tags'])
        
        obj.submodels = {k: mnl_step(m) for k, m in d['submodels'].items()}
        
        return obj

    
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
            'segmentation_column': self.segmentation_column,
            'submodels': {k: m.to_dict() for k, m in self.submodels.items()}
        }
        return d
    
    
    def get_segmentation_column(self):
        """
        Get the segmentation column from Orca.
        
        Returns
        -------
        pd.Series
        
        """
        df = orca.get_table(self.defaults.choosers).to_frame()
        return df[self.segmentation_column]
        
    
    def build_submodels(self):
        """
        Create a submodel for each category of choosers identified in the segmentation
        column. Running this method will overwrite any previous submodels. It can be run 
        as many times as desired.
        
        """
        self.submodels = {}

        col = self.get_segmentation_column()
        # TO DO - need to apply any existing chooser filters to the column first
        cats = col.astype('category').cat.categories.values
        print("Building submodels for {} categories: {}".format(len(cats), cats))
        
        for cat in cats:
            model = copy.deepcopy(self.defaults)
            
            # TO DO - with big tables, is there a more efficient way to filter the data?
            filter = "{} == '{}'".format(self.segmentation_column, cat)
            
            if isinstance(self.defaults.chooser_filters, list):
                model.chooser_filters.append(filter)
            
            elif isinstance(self.defaults.chooser_filters, str):
                model.chooser_filters = [self.defaults.chooser_filters, filter]
            
            else:
                model.chooser_filters = filter
            
            # TO DO - same for out_chooser_filters
            self.submodels[cat] = model
        
    
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
        for k, m in self.submodels.items():
            setattr(m, param, value)
    
    
    def fit_all(self):
        """
        Fit all the submodels. Build the subomdels first, if they don't exist yet. This 
        method can be run as many times as desired.
        
        """
        if (len(self.submodels) == 0):
            self.build_submodels()
        
        for k, m in self.submodels.items():
            m.fit()
        
        self.name = update_name(self.template, self.name)
    
    
    def run(self):
        """
        Convenience method (requied by template spec) that invokes `run_all()`.
        
        """
        self.run_all()
    
    
    def run_all(self):
        """
        Not yet implemented.
        
        """
        pass