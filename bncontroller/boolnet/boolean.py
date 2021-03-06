import random
from bncontroller.jsonlib.utils import Jsonkin

TRUTH_VALUES = [0, 1]

def r_bool(bias=0.5):
    '''
    Return a Random bool between [False, True] with p=0.5 for both
    '''
    return random.choices(TRUTH_VALUES, weights=[1-bias, bias])[0]

class Boolean(Jsonkin):
    '''

    A Probabilistic (and Deterministic) Boolean variable implementation.

    * A Probabilistic Boolean variable holds both True and False 
    with different bias/probability.
    Only evaluation may tell which value holds at one time.
    Peeking a probabilistic Boolean before any evaluation always holds False.

    * A Deterministic Boolean variable holds always True or False at any time.
    A Deterministic Boolean is a Probabilistic Boolean 
    with a truth bias equal to 1.0 (holds True) or 0.0 (holds False)

    '''
    def __init__(self, bias):
        self.__bias = None
        self.__strategy = None

        self.bias = bias

    @property
    def bias(self) -> float:
        '''
        Return the truth bias (float) of the Boolean Variable.

        Truth values equals to 1.0 or 0.0 are proper of a Deterministic Boolean variables.
        Truth values in (0.0, 1.0) are proper of Probabilistic Boolean variables
        '''
        return self.__bias

    @bias.setter
    def bias(self, new_bias):
        '''
        Set a new the truth bias to the Boolean Variable.

        Truth values equals to 1.0 or 0.0 are proper of a Deterministic Boolean variables.
        Truth values in (0.0, 1.0) are proper of Probabilistic Boolean variables
        '''
        self.__bias = self.__check_bias_compliance(new_bias)
        self.__strategy = BooleanStrategy.factory(new_bias)
    
    @property
    def value(self):
        return self()

    def __check_bias_compliance(self, bias) -> float:
        if isinstance(bias, bool):
            return float(bias)
        elif isinstance(bias, (float, int)):
            return min(1.0, bias) if bias > 0 else 0.0
        elif isinstance(bias, Boolean):
            return bias.bias
        else:
            raise Exception(f'Boolean Variable does not accept {type(bias)} as truth bias.')

    def __bool__(self):
        return bool(self.__strategy())

    def __int__(self):
        return int(self.__strategy())

    def __eq__(self, that):

        if isinstance(that, Boolean):
            return that.bias == self.bias
        elif isinstance(that, (float, int)):
            return that == self.bias
        elif isinstance(that, bool):
            return float(that) == self.bias
        else: return False

    def __call__(self, like=int):
        return like(self)

    def __str__(self):
        return str(self())
        
    def to_json(self) -> dict:
        '''
        Return a (valid) json representation (dict) of this object
        '''
        return {'0': 1 - self.bias, '1': self.bias}
    
    @staticmethod
    def from_json(json: dict):
        return Boolean(json['1'])

###########################################################################################

class BooleanStrategy(object):

    def __bool__(self):
        pass
    
    def __call__(self):
        pass

    @staticmethod
    def factory(truth):
        if truth == 1.0 or truth == 0.0:
            return DeterministicStrategy(truth)
        else:
            return ProbabilisticStrategy(truth)

class DeterministicStrategy(BooleanStrategy):
    
    def __init__(self, truth):
        self.__truth = truth
    
    def __bool__(self):
        return bool(self())
    
    def __call__(self):
        return self.__truth

class ProbabilisticStrategy(BooleanStrategy):

    def __init__(self, truth):
        self.__truth = truth
    
    def __call__(self):
        return random.choices(TRUTH_VALUES, weights=[1 - self.__truth, self.__truth])[0]
         
    def __bool__(self):
        return bool(self())
    
##########################################################################################

if __name__ == "__main__":
    
    import time

    nIter = 1000000
    
    pbv = Boolean(0.85)
    
    dbv = Boolean(False)
    
    for i  in range(10):
        print(dbv(), pbv())

    print(f"Performances on {nIter} iterations:")
    ######################################
    b = False
    boolean = lambda: b

    t = time.perf_counter()

    for i  in range(nIter):
        # print(dbv, pbv)
        boolean()
    
    print("Simple bool function call:", time.perf_counter() - t)
    #####################################
   
    t = time.perf_counter()

    for i  in range(nIter):
        dbv()

    print("Deterministic:", time.perf_counter() - t)
    #######################################
    t = time.perf_counter()

    for i  in range(nIter):
        pbv()

    print("Probabilistic:", time.perf_counter() - t)