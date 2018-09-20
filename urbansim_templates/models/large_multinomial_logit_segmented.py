from __future__ import print_function

import numpy as np
import pandas as pd

import orca

from .. import modelmanager
from . import LargeMultinomialLogitStep


@modelmanager.template
class SegmentedLargeMultinomialLogitStep():


    def __init__(self, defaults, segmentation_column, name=None, tage=[]):
        pass
    
    
    @classmethod
    def from_dict(cls, d):
        pass
    
    
    def to_dict(self):
        pass
    
    
    def fit_all(self):
        pass
    
    
    def run_all(self):
        pass