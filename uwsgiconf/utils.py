

def listify(src):
    """Make a list with source object if not already a list.

    :param src:
    :rtype: list

    """
    if not isinstance(src, list):
        src = [src]

    return src
