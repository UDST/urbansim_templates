from __future__ import print_function

import re
from datetime import datetime as dt

import pandas as pd

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
        raise
    
    methods = ['to_dict', 'from_dict', 'run']
    for item in methods:
        if item not in dir(cls):
            print("Expecting a '{}' method".format(item))
            return False

    try:
        d = m.to_dict()
    except:
        print("Error running 'to_dict()'")
        raise
    
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
        print("Error instantiating object with 'from_dict()' method")
        raise
    
    # TO DO - check supplemental objects? (but nothing there with unconfigured steps)
    
    return True


#####################################
## REPLACEMENT FOR ORCA BROADCASTS ##
#####################################

"""
These utilities provide functionality for merging tables using implicit join keys instead 
of Orca broadcasts. See Github issue #78 for discussion of the rationale.

"""

def validate_table(table, reciprocal=True):
    """
    Check some basic expectations about an Orca table:
    
    - Confirm that it includes a unique, named index column (a.k.a. primary key) or set 
      of columns (multi-index, a.k.a. composite key). If not, raise a ValueError.
    
    - Confirm that none of the other columns in the table share names with the index(es). 
      If they do, raise a ValueError.
    
    - If the table contains columns whose names match the index columns of other tables 
      registered with Orca, check whether they make sense as join keys. This prints a 
      status message with the number of presumptive foreign-key values that are found in 
      the primary/composite key, for evaluation by the user. 
    
    - Perform the same check for columns in _other_ tables whose names match the index 
      column(s) of _this_ table.
      
    - It doesn't currently compare indexes to indexes. (Maybe it should?)
      
    Running this will trigger loading all registered Orca tables, which may take a while. 
    Stand-alone columns will not be loaded unless their names match an index column. 
    
    Doesn't currently incorporate ``orca_test`` validation, but it might be added.
    
    Parameters
    ----------
    table : str
        Name of Orca table to validate.
    
    reciprocal : bool, default True
        Whether to also check how columns of other tables align with this one's index. 
        If False, only check this table's columns against other tables' indexes. 
    
    Returns
    -------
    bool
    
    """
    # There are a couple of reasons we're not using the orca_test library here:
    # (a) orca_test doesn't currently support MultiIndexes, and (b) the primary-key/
    # foreign-key comparisons aren't asserting anything, just printing status 
    # messages. We should update orca_test to support both, probably.
    
    if not orca.is_table(table):
        raise ValueError("Table not registered with Orca: '{}'".format(table))
    
    idx = orca.get_table(table).index
    
    # Check index has a name
    if list(idx.names) == [None]:
        raise ValueError("Index column has no name")
    
    # Check for unique column names
    for name in list(idx.names):
        if name in list(orca.get_table(table).columns):
            raise ValueError("Index names and column names overlap: '{}'".format(name))
    
    # Check for unique index values
    if len(idx.unique()) < len(idx):    
        raise ValueError("Index not unique")
    
    # Compare columns to indexes of other tables, and vice versa
    combinations = [(table, t) for t in orca.list_tables() if table != t]
    
    if reciprocal:
        combinations += [(t, table) for t in orca.list_tables() if table != t]
    
    for t1, t2 in combinations:
        col_names = orca.get_table(t1).columns
        idx = orca.get_table(t2).index
        
        if set(idx.names).issubset(col_names):
            vals = orca.get_table(t1).to_frame(idx.names).drop_duplicates()
            
            # Easier to compare multi-column values to multi-column index if we 
            # turn the values into an index as well
            vals = vals.reset_index().set_index(idx.names).index
            vals_in_idx = sum(vals.isin(idx))
            
            if len(idx.names) == 1:
                idx_str = idx.names[0]
            else:
                idx_str = '[{}]'.format(','.join(idx.names))
            
            print("'{}.{}': {} of {} unique values are found in '{}.{}' ({}%)"\
                    .format(t1, idx_str, 
                            vals_in_idx, len(vals), 
                            t2, idx_str, 
                            round(100*vals_in_idx/len(vals))))

    return True


def validate_all_tables():
    """
    Validate all tables registered with Orca. See ``validate_table()`` above.
    
    Returns
    -------
    bool
    
    """
    for t in orca.list_tables():
        validate_table(t, reciprocal=False)


def merge_tables(tables, columns=None):
    """
    Merge two or more tables into a single DataFrame. 
    
    All the data will eventually be merged onto the first table in the list. In each 
    merge stage, we'll refer to the right-hand table as the "source" and the left-hand 
    one as the "target". 
    
    Tables are merged using ModelManager schema rules: The source table must have a 
    unique index, and the target table must have a column with a matching name, which 
    will be used as the join key. Multi-indexes are fine, but all of the index columns 
    need to be present in the target table.
    
    The last table in the list is the initial source. The algorithm searches backward
    through the list for a table that qualifies as a target. The source table is left-
    joined onto the target, and then the algorithm continues with the second-to-last 
    table as the new source. 
    
    Example 1: Tables A and B share join keys. Tables B and C share join keys. Merging 
    [A, B, C] will left-join C onto B, and then left-join the result onto A. 
    
    Example 2: Tables A and B share join keys. Tables A and C also share join keys, but 
    tables B and C don't. Merging [A, B, C] will left-join C onto A, and then left-join 
    B onto the result of the first join.
    
    If you provide a list of ``columns``, the output table will be limited to columns in 
    this list. The index(es) of the left-most table will always be retained, but it's a 
    good practice to list them anyway. Column names not found will be ignored.

    If two tables contain columns with identical names (other than join keys), they can't  
    be automatically merged. If the columns are just incidental and not needed in the 
    final output, you can perform the merge by providing a ``columns`` list that excludes 
    them.
    
    A note about data types: They will be retained, but if NaN values need to be added 
    (e.g. if some identifiers from the target table aren't found in the source table), 
    data may need to be cast to a type that allows missing values. For better control 
    over this, see ``urbansim_templates.data.ColumnFromBroadcast()``.
        
    Parameters
    ----------
    tables : list of str, orca.DataFrameWrapper, orca.TableFuncWrapper, or pd.DataFrame
        Two or more tables to merge. Types can be mixed and matched.
    
    columns : list of str, optional
        Names of columns to retain in the final output.
    
    Returns
    -------
    pd.DataFrame
    
    """
    while len(tables) > 1:
        # last table becomes the source
        source = get_df(tables[-1], columns)
        keys = list(source.index.names)
        
        # search for target table
        target_position = None
        for i in range(len(tables)-2, -1, -1):
            if set(keys).issubset(set(all_cols(tables[i]))):
                target_position = i
                target_columns = columns + keys if columns is not None else None
                target = get_df(tables[i], target_columns)
                break
        
        if target_position is None:
            msg = "Could not find a target to merge table {} onto".format(len(tables))
            raise ValueError(msg)

        # merge source onto target
        merged = target.join(source, on=keys, how='left')  # pandas 0.23+ for on=keys
        
        tables = tables[:-1]
        tables[target_position] = merged

    # drop final merge keys if not needed
    merged = trim_cols(merged, columns)
    
    return merged
    


###############################
## TEMPLATE HELPER FUNCTIONS ##
###############################

def get_df(table, columns=None):
    """
    Returns a table as a ``pd.DataFrame``. Input can be an Orca table name, 
    ``orca.DataFrameWrapper``, ``orca.TableFuncWrapper``, or ``pd.DataFrame``.
    
    Optionally, columns can be limited to those that appear in a list of names. The list 
    may contain duplicates or columns not in the table. Index(es) will always be
    retained, but it's a good practice to list them anyway.
    
    Parameters
    ----------
    table : str, orca.DataFrameWrapper, orca.TableFuncWrapper, or pd.DataFrame
    columns : list of str, optional
    
    Returns
    -------
    pd.DataFrame
    
    """
    if type(table) not in [str, 
                           orca.DataFrameWrapper, 
                           orca.TableFuncWrapper, 
                           pd.DataFrame]:
        raise ValueError("Table has unsupported type: {}".format(type(table)))
    
    if type(table) == pd.DataFrame:
        return trim_cols(table, columns)
    
    elif type(table) == str:
        table = orca.get_table(table)
    
    if columns is not None:
        # Orca requires column list to be unique and existing, or None
        columns = list(set(columns) & set(table.columns))
    
    return table.to_frame(columns=columns)
    

def all_cols(table):
    """
    Returns a list of all column names in a table, including index(es). Input can be an 
    Orca table name, ``orca.DataFrameWrapper``, ``orca.TableFuncWrapper``, or 
    ``pd.DataFrame``.
    
    Parameters
    ----------
    table : str, orca.DataFrameWrapper, orca.TableFuncWrapper, or pd.DataFrame
    
    Returns
    -------
    list of str
    
    """
    if type(table) not in [str, 
                           orca.DataFrameWrapper, 
                           orca.TableFuncWrapper, 
                           pd.DataFrame]:
        raise ValueError("Table has unsupported type: {}".format(type(table)))

    if type(table) == str:
        table = orca.get_table(table)
    
    return list(table.index.names) + list(table.columns)
    

def cols_in_expression(expression):
    """
    Extract all possible column names from a ``df.eval()``-style expression. 
    
    This is achieved using regex to identify tokens in the expression that begin with a
    letter and contain any number of alphanumerics or underscores, but do not end with an
    opening parenthesis. This excludes function names, but would not exclude constants
    (e.g. "pi"), which are semantically indistinguishable from column names.
    
    Parameters
    ----------
    expression : str
    
    Returns
    -------
    cols : list of str
    
    """
    return re.findall(r'[a-zA-Z_][a-zA-Z0-9_]*(?!\()', expression)


def trim_cols(df, columns=None):
    """
    Limit a DataFrame to columns that appear in a list of names. List may contain 
    duplicates or names not in the DataFrame. Index(es) of the DataFrame will always be 
    retained, but it's a good practice to list them anyway. If ``columns`` is None, all 
    columns are retained. Returns the original DataFrame, not a copy. 
    
    Parameters
    ----------
    df : pd.DataFrame
    columns : list of str, optional
    
    Returns
    -------
    pd.DataFrame
    
    """
    if columns is None:
        return df
    
    cols = set(columns) & set(df.columns)  # unique, existing columns
    return df[list(cols)]
    

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
    Generate a ``pd.DataFrame`` for model estimation or simulation. Automatically loads 
    tables from Orca, merges them, and removes columns not referenced in a model 
    expression or data filter. Additional columns can be requested.
    
    If filters are provided, the output will include only rows that match the filter
    criteria. 
    
    See ``urbansim_templates.utils.merge_tables()`` for a detailed description of how 
    the merges are performed.
    
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
    
    colnames = None  # this will get all columns
    if (model_expression is not None) or (extra_columns is not None):
        colnames = list(set(columns_in_formula(model_expression) + \
                            columns_in_filters(filters) + to_list(extra_columns)))

    if not isinstance(tables, list):
        df = get_df(tables, colnames)
    
    else:
        df = merge_tables(tables, colnames)
    
    df = apply_filter_query(df, filters)
    return df
    
    
def update_column(table, column, data, fallback_table=None, fallback_column=None):
    """
    Update an Orca column. If it doesn't exist yet, add it to the wrapped DataFrame. 
    Values will be aligned using the indexes if possible.
    
    Data types: If the column already exists, new values will be cast to match the 
    existing data type. If the column is new, it will retain the data type of the 
    pd.Series that's passed to this function -- unless it doesn't fully align with the 
    table's index, in which case it may be cast to allow missing values (e.g. from int 
    to float).
    
    Parameters
    ----------
    table : str or list of str
        Name of Orca table to update. If list, the first element will be used.
    
    column : str
        Name of existing column to update, or new column to create. Cannot be an index.
        
    data : pd.Series
        Column of data to update or add. 
        
    fallback_table : str or list of str
        Name of Orca table to use if ``table`` evaluates to None.
    
    fallback_column : str
        Name of Orca column to use if ``column`` evaluates to None.
        
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
        dfw.update_col(column, data)  # adds column
    
    else:
        dfw.update_col_from_series(column, data, cast=True)  # updates existing column
    

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
    
