import logging

from cursive_writer.utils.color_utils import fmt_cn


def iterate_double_list(the_list):
    """Iterate over the elements of a list of lists

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for inner_list in the_list:
        for element in inner_list:
            yield element


def enumerate_double_list(the_list):
    """Enumerate the content of a list of lists, providing both indexes

    the_list = [[e0, e1, e2], [e3, e4]]
    """
    for i, inner_list in enumerate(the_list):
        for j, element in enumerate(inner_list):
            yield i, j, element

def find_free_index(folder, base_name_fmt):
    """Find the first free name
    """
    logg = logging.getLogger(f"c.{__name__}.find_free_index")
    logg.setLevel("TRACE")
    logg.info(f"Start {fmt_cn('find_free_index', 'a2')}")
    for i in range(1000):
        file_name = folder / base_name_fmt.format(i)
        if file_name.exists():
            logg.debug(f"Found file_name: {file_name}")
        else:
            logg.debug(f"Empty file_name: {file_name}")
            return i
            
            
    
