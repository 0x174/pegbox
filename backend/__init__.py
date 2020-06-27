'''
backend/__init__.py

Top level import for all objects in the backend. Probably a little bit naive
and would generate some issues at scale as they regard to circular importation
and datastructures that would depend on each other.
'''

from .datastructures import *
from .api_interactions import *
from .parsing import *
from .solvers import *

