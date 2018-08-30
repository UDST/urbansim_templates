from __future__ import print_function


def version_parse(v):
    """
    Parses a version string into its component parts. String is expected to follow the 
    pattern "0.1.1.dev0", which would be parsed into (0, 1, 1, 0). The first two 
    components are required, and the latter two are assumed to be zero if missing.
    
    Parameters
    ----------
    v : str
        Version string using syntax described above.
    
    Returns
    -------
    tuple of four integers
    
    """
    v4 = 0
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
    Version syntax is expected to follow this pattern: 0.1.dev0 -> 0.1.dev1 -> 0.1 ->
    0.1.1.dev0 -> 0.1.1 -> 0.2 -> 1.0, etc.
    
    Parameters
    ----------
    a : str
        First version string, should be formatted as above. Required.
    b : str
        Second version string, should be formatted as above. Required.
    
    Returns
    -------
    bool
    
    """
    
    
    
    # Parse each of the strings into four components: x.x.(x).dev(x), where the first two
    # values are always present and the latter two are assumed to be zero if missing, 
    # and compare each in turn
    
    