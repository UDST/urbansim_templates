from __future__ import print_function

from urbansim_templates import __version__


class CoreTemplateSettings():
    """
    Stores standard parameters and logic used by all templates. Parameters can be passed 
    to the constructor or set as attributes.
    
    Parameters
    ----------
    name : str, optional
        Name of the configured template instance.
    
    tags : list of str, optional
        Tags associated with the configured template instance.
    
    notes : str, optional
        Notes associates with the configured template instance.
    
    autorun : bool, optional
        Whether to run the configured template instance automatically when it's 
        registered or loaded by ModelManager. The overall default is False, but the 
        default can be overriden at the template level.
    
    template : str
        Name of the template class associated with a configured instance.
    
    template_version : str
        Version of the template class package.
    
    Attributes
    ----------
    modelmanager_version : str
        Version of the ModelManager package that created the CoreTemplateSettings. 
    
    """
    def __init__(self,
            name = None,
            tags = [],
            notes = None,
            autorun = False,
            template = None,
            template_version = None):
        
        self.name = name
        self.tags = tags
        self.notes = notes
        self.autorun = autorun
        self.template = template
        self.template_version = template_version
        
        # automatic attributes
        self.modelmanager_version = __version__
    
    
    @classmethod
    def from_dict(cls, d):
        """
        Create a class instance from a saved dictionary representation.
        
        Parameters
        ----------
        d : dict
        
        Returns
        -------
        meta : CoreTemplateSettings
        
        """
        obj = cls(
            name = d['name'],
            tags = d['tags'],
            notes = d['notes'],
            autorun = d['autorun'],
            template = d['template'],
            template_version = d['template_version'],
        )
        return d
    
    
    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Returns
        -------
        d : dict
        
        """
        d = {
            'name': self.name,
            'tags': self.tags,
            'notes': self.notes,
            'autorun': self.autorun,
            'template': self.template,
            'template_version': self.template_version,
            'modelmanager_version': self.modelmanager_version,
        }

