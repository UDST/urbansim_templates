from __future__ import print_function


def v_parse(v):
    """
    Parses a version string into its component integers so they can be compared. Version
    syntax is expected to follow the pattern 0.1.1.dev0
    
    """


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
    
    