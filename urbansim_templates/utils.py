from __future__ import print_function


def version_parse(v):
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
    a = version_parse(a)
    b = version_parse(b)
    
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
    
    