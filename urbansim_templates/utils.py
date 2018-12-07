from __future__ import print_function

from datetime import datetime as dt

import orca
from urbansim.models import util


################################
## SPEC AND FORMAT MANAGEMENT ##
################################

def validate_template(cls):
    """
    Checks whether a template class meets the basic expectations for working with 
    ModelManager, to aid in development and testing.
    
    Looks for 'to_dict', 'from_dict', and 'run' methods, and 'name', 'tags', 'template',
    and 'template_version' attributes. Checks that an object can be instantiated without 
    arguments, plus some additional behaviors. See documentation for a full description 
    of ModelManager specs and guidelines.
    
    There are many behaviors this does NOT check, because we don't know what particular
    parameters are expected and valid for a given template. For example, saving a 
    configured model step and reloading it should produce an equivalent object, but this
    needs to be checked in template-specific unit tests.
    
    Parameters
    ----------
    cls : class
        Template class.
    
    Returns
    -------
    bool
    
    """
    try:
        m = cls()
    except:
        print("Error instantiating object without arguments")
        return False
    
    methods = ['to_dict', 'from_dict', 'run']
    for item in methods:
        if item not in dir(cls):
            print("Expecting a '{}' method".format(item))
            return False

    try:
        d = m.to_dict()
    except:
        print("Error running 'to_dict()'")
        return False
    
    params = ['name', 'tags', 'template', 'template_version']
    for item in params:
        if item not in d:
            print("Expecting a '{}' key in dict representation".format(item))
            return False
    
    if (d['template'] != m.__class__.__name__):
        print("Expecting 'template' value in dict to match the class name")
        return False

    try:
        cls.from_dict(m.to_dict())
    except:
        print("Error passing dict to 'from_dict()' method")
        return False
    
    # TO DO - check supplemental objects? (but nothing there with unconfigured steps)
    
    return True


###############################
## TEMPLATE HELPER FUNCTIONS ##
###############################

def update_name(template, name=None):
    """
    Generate a name for a configured model step, based on its template class and the 
    current timestamp. But if a custom name has already been provided, return that 
    instead. (A name is judged to be custom if it does not contain the class type.)
            
    Parameters
    ----------
    template : str
        Template class name.
    
    name : str, optional
        Existing name for the configured model step.
    
    Returns
    -------
    str
    
    """
    if (name is None) or (template in name):
        return template + '-' + dt.now().strftime('%Y%m%d-%H%M%S')
    else:
        return name


def validate_colnames(tables, fallback_tables=None, model_expression=None, filters=None, 
        extra_columns=None):
    """
    Confirm that the column names referenced in a model expression and filters are unique
    within the set of tables the columns are being drawn from. Join keys are excepted.
    
    Depending on how merges are specified, duplicate column names may result in (a) an 
    error, (b) silently dropped columns, or (c) silently renamed columns. Checking that
    relevant column names are unique before merges helps us avoid this.
    
    Parameters
    ----------
    tables : str or list of str
        Name of table(s) to draw data from.
    
    fallback_tables : str or list of str, optional
        Table(s) to use if first parameter evaluates to `None`.
        
    model_expression : str
        Model expression to be evaluated using the merged data.
        
    filters : str or list of str, optional
        Filter(s) to be applied to the merged data.
    
    extra_columns : str or list of str, optional
        Additional column names expected to be unique.
        
    Returns
    -------
    bool
        Returns True if column names are unique, and raises a ValueError if not.
        
    """
    if tables is None:
        tables = fallback_tables
    
    if not isinstance(extra_columns, list):
        extra_columns = [extra_columns]
    
    colnames = set(extra_columns + \
            util.columns_in_filters(filters) + \
            util.columns_in_formula(model_expression))
    
    print(colnames)
    
    for c in colnames:
        col_in_table = []
        
        for t in tables:
            dfw = orca.get_table(t)  # DataFrameWrapper
            if (c in dfw.columns) or (c in dfw.index.names):
                col_in_table.append(t)
        
        if len(col_in_table) > 1:
            raise ValueError("Ambiguous merge: column '{}' appears in tables '{}'"\
                    .format(c, ', '.join(col_in_table)))
    
    return True
    
    # get broadcasts from orca, and allow duplicate names if they're join keys


########################
## VERSION MANAGEMENT ##
########################

def parse_version(v):
    """
    Parses a version string into its component parts. String is expected to follow the 
    pattern "0.1.1.dev0", which would be parsed into (0, 1, 1, 0). The first two 
    components are required. The third is set to 0 if missing, and the fourth to None.
    
    Parameters
    ----------
    v : str
        Version string using syntax described above.
    
    Returns
    -------
    tuple with format (int, int, int, int or None)
    
    """
    v4 = None
    if 'dev' in v:
        v4 = int(v.split('dev')[1])
        v = v.split('dev')[0]  # 0.1.dev0 -> 0.1.
        
        if (v[-1] == '.'):
            v = v[:-1]  # 0.1. -> 0.1
        
    v = v.split('.')
    
    v3 = 0
    if (len(v) == 3):
        v3 = int(v[2])
    
    v2 = int(v[1])
    v1 = int(v[0])
    
    return (v1, v2, v3, v4)
    

def version_greater_or_equal(a, b):
    """
    Tests whether version string 'a' is greater than or equal to version string 'b'.
    Version syntax should follow the pattern described for `version_parse()`. 
    
    Note that 'dev' versions are pre-releases, so '0.2' < '0.2.1.dev5' < '0.2.1'.
        
    Parameters
    ----------
    a : str
        First version string, formatted as described in `version_parse()`. 
    b : str
        Second version string, formatted as described in `version_parse()`. 
    
    Returns
    -------
    boolean
    
    """
    a = parse_version(a)
    b = parse_version(b)
    
    if (a[0] > b[0]):
        return True
    
    elif (a[0] == b[0]):
        if (a[1] > b[1]):
            return True
            
        elif (a[1] == b[1]):
            if (a[2] > b[2]):
                return True
            
            elif (a[2] == b[2]):
                if (a[3] == None):
                    return True
                
                elif (b[3] == None):
                    return False
                
                elif (a[3] >= b[3]):
                    return True
    
    return False
    
