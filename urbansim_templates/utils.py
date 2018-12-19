from __future__ import print_function

from datetime import datetime as dt

import orca
from urbansim.models.util import (apply_filter_query, columns_in_filters, 
        columns_in_formula)


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

def to_list(items):
    """
    In many places we accept either a single string or a list of strings. This function
    normalizes None -> [None], str -> [str], and leaves lists unchanged.
    
    Parameters
    ----------
    items : str, list, or None

    Returns
    -------
    list
    
    """
    if not isinstance(items, list):
        items = [items]
    
    return items


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


def get_data(tables, fallback_tables=None, filters=None, model_expression=None, 
        extra_columns=None):
    """
    Generate a pd.DataFrame from one or more tables registered with Orca. Templates should 
    call this function immediately before the data is needed, so that it's as up-to-date 
    as possible.
    
    If filters are provided, the output will include only rows that match the filter
    criteria. 
    
    Default behavior is for the output to inclue all columns. If a model_expression and/or
    extra_columns is provided, non-relevant columns will be dropped from the output.
    Relevant columns include any mentioned in the model expression, filters, or list of 
    extras. Join keys will *not* be included in the final output even if the data is drawn
    from multiple tables, unless they appear in the model expression or filters as well.
    
    If a named column is not found in the source tables, it will just be skipped. This is 
    to support use cases where data is assembled separately for choosers and alternatives 
    and then merged together -- the model expression would include terms from both sets 
    of tables.
    
    Duplicate column names are not recommended -- columns are expected to be unique within 
    the set of tables they're being drawn from, with the exception of join keys. If column 
    names are repeated, current behavior is to follow the Orca default and keep the 
    left-most copy of the column. This may change later and should not be relied on. 
    
    Parameters
    ----------
    tables : str or list of str
        Orca table(s) to draw data from.
    
    fallback_tables : str or list of str, optional
        Table(s) to use if first parameter evaluates to `None`. (This option will be 
        removed shortly when estimation and simulation settings are separated.)
    
    filters : str or list of str, optional
        Filter(s) to apply to the merged data, using `pd.DataFrame.query()`.
    
    model_expression : str, optional
        Model expression that will be evaluated using the output data. Only used to drop 
        non-relevant columns. PyLogit format is not yet supported.
    
    extra_columns : str or list of str, optional
        Columns to include, in addition to any in the model expression and filters. (If 
        this and the model_expression are both None, all columns will be included.)

    Returns
    -------
    pd.DataFrame
    
    """
    if tables is None:
        tables = fallback_tables
    
    tables = to_list(tables)
    colnames = None  # this will get all columns from Orca utilities
    
    if (model_expression is not None) or (extra_columns is not None):
        colnames = set(columns_in_formula(model_expression) + \
                       columns_in_filters(filters) + to_list(extra_columns))
    
        # skip cols not found in any of the source tables - have to check for this 
        # explicitly because the orca utilities will raise an error if we request column
        # names that aren't there
        all_cols = []
        for t in tables:
            dfw = orca.get_table(t)
            all_cols += list(dfw.index.names) + list(dfw.columns)
    
        colnames = [c for c in colnames if c in all_cols]
    
    if len(tables) == 1:
        df = orca.get_table(table_name=tables[0]).to_frame(columns=colnames)
    
    else:
        df = orca.merge_tables(target=tables[0], tables=tables, columns=colnames)

    if colnames is not None:
        if len(df.columns) > len(colnames):
            df = df[colnames]

    df = apply_filter_query(df, filters)
    return df
    
    
def update_column(table, column, data, fallback_table=None, fallback_column=None):
    """
    Update an Orca column. If it doesn't exist yet, add it to the table.
    
    If the column already exists, 'data' will be cast to match the column's data type. If 
    the column needs to be created, it will be given the same data type as 'data'.
    
    Require an index?
    
    Parameters
    ----------
    table : str or list of str
        Name of an Orca table. If list, the first element will be used.
    
    column : str
        Name of a column in the table. Cannot be an index.
        
    data : pd.Series
        Should either align with the index of the table, or have the same number of rows.
        
    fallback_table : str or list of str
        Name of Orca table to use if 'table' evaluates to None.
    
    fallback_column : str
        Name of Orca column to use if 'column' evaluates to None.
        
    Returns
    -------
    None
    
    """
    if table is None:
        table = fallback_table
    
    if isinstance(table, list):
        table = table[0]
    
    if column is None:
        column = fallback_column
    
    dfw = orca.get_table(table)
    
    if column not in dfw.columns:
        dfw.update_col(column, data)
    
    else:
        dfw.update_col_from_series(column, data, cast=True)
    

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
    
