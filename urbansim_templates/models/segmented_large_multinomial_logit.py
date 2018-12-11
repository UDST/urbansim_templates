from __future__ import print_function

import copy

import numpy as np
import pandas as pd

import orca
from urbansim.models.util import apply_filter_query

from ..__init__ import __version__
from ..utils import get_data, update_name
from .. import modelmanager
from . import LargeMultinomialLogitStep
from .shared import TemplateStep


@modelmanager.template
class SegmentedLargeMultinomialLogitStep(TemplateStep):
    """
    This template automatically generates a set of LargeMultinomialLogitStep submodels
    corresponding to "segments" or categories of choosers. The submodels can be directly 
    accessed and edited. 
    
    Running 'build_submodels()' will create a submodel for each category of choosers
    identified in the segmentation column. The submodels are implemented using filter
    queries. 
    
    Once they are generated, the 'submodels' property contains a dict of
    LargeMultinomialLogitStep objects, identified by category name. You can edit their 
    properties as needed, fit them individually, etc. 
    
    Editing a property in the 'defaults' object will update all the submodels at once, 
    while leaving customizations to other properties intact.
    
    Parameters
    ----------
    defaults : LargeMultinomialLogitStep, optional
        Object containing initial parameter values for the submodels. Values for
        'choosers', 'alternatives', and 'choice_column' are required to generate 
        submodels, but do not have to be provided when the object is created.
    
    segmentation_column : str, optional
        Name of a column of categorical values in the 'defaults.choosers' table. Any data 
        that can be interpreted by Pandas as categorical is valid. This is required to 
        generate submodels, but does not have to be provided when the object is created.
    
    name : str, optional
        Name of the model step.
    
    tags : list of str, optional
        Tags associated with the model step. 
    
    """
    def __init__(self, defaults=None, segmentation_column=None, name=None, tags=[]):
        
        if defaults is None:
            defaults = LargeMultinomialLogitStep()
        
        self.defaults = defaults
        self.defaults.bind_to(self.update_submodels)
        
        self.segmentation_column = segmentation_column
        
        self.name = name
        self.tags = tags
        
        self.template = self.__class__.__name__
        self.template_version = __version__
        
        # Properties to be filled in by build_submodels() or from_dict()
        self.submodels = {}
    
    
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
        Get the column of segmentation values from Orca. Chooser and alternative filters 
        are applied to identify valid observations.
                
        Returns
        -------
        pd.Series
        
        """
        obs = get_data(tables = self.defaults.choosers,
                       filters = self.defaults.chooser_filters,
                       extra_columns = [self.defaults.choice_column, 
                                        self.segmentation_column])
        
        alts = get_data(tables = self.defaults.alternatives,
                        filters = self.defaults.alt_filters)
        
        df = pd.merge(obs, alts, how='inner',
                      left_on=self.defaults.choice_column, right_index=True)
        
        return df[self.segmentation_column]
        
    
    def build_submodels(self):
        """
        Create a submodel for each category of choosers identified in the segmentation
        column. Only categories with at least one observation remaining after applying
        chooser and alternative filters will be included. 
        
        Running this method will overwrite any previous submodels.
        
        """
        self.submodels = {}
        submodel = LargeMultinomialLogitStep.from_dict(self.defaults.to_dict())

        col = self.get_segmentation_column()

        if (len(col) == 0):
            print("Warning: No valid observations after applying the chooser and "+
                  "alternative filters")
            return
        
        cats = col.astype('category').cat.categories.values

        print("Building submodels for {} categories: {}".format(len(cats), cats))
        
        for cat in cats:
            m = copy.deepcopy(submodel)
            seg_filter = "{} == '{}'".format(self.segmentation_column, cat)
            
            if isinstance(m.chooser_filters, list):
                m.chooser_filters += [seg_filter]
            
            elif isinstance(m.chooser_filters, str):
                m.chooser_filters = [m.chooser_filters, seg_filter]
            
            else:
                m.chooser_filters = seg_filter
            
            # TO DO - same for out_chooser_filters, once we handle simulation
            self.submodels[cat] = m
        
    
    def update_submodels(self, param, value):
        """
        Updates a property across all the submodels. This method is bound to the 
        `defaults` object and runs automatically when one of its properties is changed.
        
        Note that the `chooser_filters` and `alt_filters` properties cannot currently be 
        updated this way, because they can affect the model segmentation. If you are 
        confident the changes are valid, you can edit the submodels directly. Otherwise,
        you can regenerate them using updated defaults by running `build_submodels()`.
        
        Parameters
        ----------
        param : str
            Property name.
        value : anything
        
        """
        if (param in ['chooser_filters', 'alt_filters']) & (len(self.submodels) > 0):
            print("Warning: Changing '{}' can affect the model segmentation. Changes " +
                  "have been saved to 'defaults' but not to the submodels. To " +
                  "regenerate them using the new defaults, run 'build_submodels()'."\
                  .format(param))
            return
        
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
            print(' SEGMENT: {0} = {1} '.format(
                self.segmentation_column, str(k)).center(70, '#'))
            m.fit()
        
        self.name = update_name(self.template, self.name)
    
    
    def run(self):
        """
        Convenience method (requied by template spec) that invokes `run_all()`.
        
        """
        self.run_all()
    
    
    def run_all(self):
        """
        Run all the submodels.
        
        """
        for k, m in self.submodels.items():
            print(' SEGMENT: {0} = {1} '.format(
                self.segmentation_column, str(k)).center(70, '#'))
            m.run()
