from urbansim_templates import __version__


class OutputColumnSettings():
    """
    Stores standard parameters and logic used by templates that generate or modify
    columns. Parameters can be passed to the constructor or set as attributes.
    
    Parameters
    ----------
    column_name : str, optional
        Name of the Orca column to be created or modified. Generally required before
        running a configured template.
    
    table : str, optional
        Name of Orca table the column will be associated with. Generally required before
        running the configured template.
    
    data_type : str, optional
        Python type or ``numpy.dtype`` to case the column's values to.
    
    missing_values : str or numeric, optional
        Value to use for rows that would otherwise be missing.
    
    cache : bool, default False
        Whether to cache column values after they are calculated
    
    cache_scope : 'step', 'iteration', or 'forever', default 'forever'
        How long to cache column values for (ignored if ``cache`` is False).
    
    """
    # TO DO: say something about Orca defaults and about core vs. computed columns.

    def __init__(self,
            column_name = None,
            table = None,
            data_type = None,
            missing_values = None,
            cache = False,
            cache_scope = 'forever'):
        
        self.column_name = column_name
        self.table = table
        self.data_type = data_type
        self.missing_values = missing_values
        self.cache = cache
        self.cache_scope = cache_scope
        
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
        meta : OutputColumnSettings
        
        """
        obj = cls(
            column_name = d['column_name'],
            table = d['table'],
            data_type = d['data_type'],
            missing_values = d['missing_values'],
            cache = d['cache'],
            cache_scope = d['cache_scope'],
        )
        return obj
    
    
    def to_dict(self):
        """
        Create a dictionary representation of the object.
        
        Returns
        -------
        d : dict
        
        """
        d = {
            'column_name': self.column_name,
            'table': self.table,
            'data_type': self.data_type,
            'missing_values': self.missing_values,
            'cache': self.cache,
            'cache_scope': self.cache_scope,
            'modelmanager_version': self.modelmanager_version,
        }
        return d

