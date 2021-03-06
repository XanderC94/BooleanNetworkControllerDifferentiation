'''
'''
import random
from bncontroller.boolnet.utils import random_neighbors_generator
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.boolnet.boolean import r_bool
from bncontroller.boolnet.factory import RBNFactory

def template_selector_generator(
        N: int, K: int, P: float, Q: float, I: int, O: int,
        F=lambda n, o: random_neighbors_generator(n, o, self_loops=False)):
    
    _N = list(map(str, range(N)))
    _I = list(map(str, range(I))) 
    _O = list(map(str, range(I, I + O))) 
    _K = list(K for _ in _N)

    return RBNFactory(_N, _K, P, Q, _I, _O, F)

##############################################################################

def test_contraints(obj: object, constraints_tests: list) -> bool:
    '''
    Sequentially checks constraints satisfaction tests on the given object.

    Test order is important, each test is applied if and only if
    the previous one was successful.

    Empty test list always hold success (True)

    '''

    # Recursive
    # if not constraints_tests:
    #     return True

    # return (
    #     test_contraints(obj, constraints_tests[1:]) 
    #     if constraints_tests[0](obj) 
    #     else False
    # )

    res = bool(constraints_tests)

    while constraints_tests and res:
        res = res and constraints_tests[0](obj)
        constraints_tests = constraints_tests[1:]

    return res

#############################################################################

class udict(object):

    def __init__(self, **kwargs):

        self.__dict = dict(**kwargs)

    def __setitem__(self, key, item):

        if item is None:
            raise Exception('None attractor.')
        # elif isinstance(item, list) and len(item) > 1:
        #     raise Exception('Multiple attractors at once.')
        elif key in self.__dict and self.__dict[key] != item:
            raise Exception('Mismatching attractors for the same input on different initial states.')
        elif item in set(v for k, v in self.__dict.items() if k != key):
            raise Exception('Duplicate attractor for different input values.')
        elif key not in self.__dict:
            self.__dict[key] = item
    
    def update(self, key, item):
        if item is None or (
            # isinstance(item, list) and len(item) > 1) or (
            key in self.__dict and self.__dict[key] != item) or (
                item in set(v for k, v in self.__dict.items() if k != key)):

            return False

        elif key not in self.__dict:
            self.__dict[key] = item
        
        return True

    def __getitem__(self, key):
        return self.__dict[key] if key in self.__dict else None
    
    def __contains__(self, key):
        return key in self.__dict
    
    def values(self):
        return self.__dict.values()
    
    def keys(self):
        return self.__dict.keys()
    
    def __iter__(self):
        for k in self.__dict:
            yield k