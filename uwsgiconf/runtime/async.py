# This module is for backward compatibility:
# since in python 3.7+ `async` is a keyword it cannot be used in imports.
from warnings import warn

from .asynced import *

warn('runtime.async module is deprecated. Please use runtime.asynced', DeprecationWarning)
