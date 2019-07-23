from bncontroller.jsonlib.utils import Jsonkin
import json, random, math, enum, numpy as np
from collections import defaultdict
from pathlib import Path

class Point3D(Jsonkin):

    def __init__(self, x:float, y:float, z:float):

        self.x = x
        self.y = y
        self.z = z

    def __check_instance(self, that):
        if isinstance(that, Point3D):
            return that
        elif isinstance(that, dict):
            return Point3D.from_json(that)
        elif isinstance(that, (tuple, list)):
            return Point3D.from_tuple(that)
        else:
            raise Exception('Invalid 3D Point representation.')

    def dist(self, that) -> float:
        
        _that = self.__check_instance(that)

        return math.sqrt(
            (self.x - _that.x)**2 + (self.y - _that.y)**2 + (self.z - _that.z)**2
        )
    
    def to(self, x, y, z):
        self.x = x
        self.z = z
        self.y = y
        return self

    def __iter__(self):
        for c in [self.x, self.y, self.z]: 
            yield c
        
    def __add__(self, that):
        return Point3D(self.x + that.x, self.y + that.y, self.z + that.z)
    
    def __abs__(self):
        return Point3D(abs(self.x), abs(self.y), abs(self.z))

    def __eq__(self, that):
        if isinstance(that, Point3D):
            return self.x == that.x and self.y == that.y and self.z == that.z
        else:
            return False

    def to_json(self) -> dict:
        return vars(self)

    def to_tuple(self) -> tuple:
        return tuple(self.x, self.y, self.z)

    @staticmethod
    def from_json(json:dict):
        return Point3D(
            json['x'],
            json['y'],
            json['z']
        )

    @staticmethod
    def from_tuple(coordinates):
        return Point3D(coordinates[0], coordinates[1], coordinates[2])

#####################################################################

class Axis(enum.Enum):
    X = lambda p: p.to(0.0, p.y, p.z)
    Y = lambda p: p.to(p.x, 0.0, p.z)
    Z = lambda p: p.to(p.x, p.y, 0.0)
    NONE = lambda p: p

class Quadrant(enum.Enum):
    PPP = lambda p: abs(p)
    PPN = lambda p: p.to( abs(p.x),  abs(p.y), -abs(p.z))
    PNN = lambda p: p.to( abs(p.x), -abs(p.y), -abs(p.z))
    NNN = lambda p: p.to(-abs(p.x), -abs(p.y), -abs(p.z))
    NNP = lambda p: p.to(-abs(p.x), -abs(p.y),  abs(p.z))
    NPP = lambda p: p.to(-abs(p.x),  abs(p.y),  abs(p.z))
    NPN = lambda p: p.to(-abs(p.x),  abs(p.y), -abs(p.z))
    PNP = lambda p: p.to( abs(p.x), -abs(p.y),  abs(p.z))
    ANY = lambda p: p

def r_point3d(O = Point3D(0.0,0.0,0.0), R = 1.0, axis = Axis.NONE, quadrant=Quadrant.ANY):

    r = R * math.sqrt(np.random.uniform(0.0, 1.0))

    phi = math.acos(1 - 2 * np.random.uniform(0.0, 1.0))

    theta = np.random.uniform(0.0, 1.0) * 2 * math.pi

    P = Point3D(
        x = r * math.cos(theta) * math.sin(phi), 
        y = r * math.sin(theta) * math.sin(phi),
        z = r * math.cos(phi)
    )

    return O + axis(quadrant(P))

##################################################################

def generate_spawn_points(config):

    spawn_points = dict()

    # Generate Evaluation Point
    spawn_points['agent_spawn_points'] = (
        [config.sim_agent_position]
        if not config.eval_n_agent_spawn_points else [
            r_point3d(
                O=config.sim_agent_position, 
                R=config.eval_agent_spawn_radius_m, 
                axis=Axis.Y, 
                quadrant=Quadrant.PPN
            )
            for _ in range(config.eval_n_agent_spawn_points)    
        ]
    )

    # Generate Light Position
    spawn_points['light_spawn_points'] = (
        [config.sim_light_position]
        if not config.eval_n_light_spawn_points else [
            r_point3d(
                O=config.sim_light_position, 
                R=config.eval_light_spawn_radius_m, 
                axis=Axis.Y, 
                quadrant=Quadrant.PPN
            )
            for _ in range(config.eval_n_light_spawn_points)    
        ]
    )

    # Generate Evaluation yRot
    spawn_points['agent_yrots'] = (
        [config.sim_agent_yrot_rad]
        if not config.eval_agent_n_yrot_samples else np.arange(
            config.eval_agent_yrot_start_rad,
            2*math.pi + config.eval_agent_yrot_start_rad,
            2*math.pi / config.eval_agent_n_yrot_samples
        ) if config.eval_agent_n_yrot_samples > 0 else np.random.uniform(
            0.0, 2*math.pi, max(1, config.eval_n_agent_spawn_points)
        )
    )

    return spawn_points
    
#########################################################################

class SimulationStepData(Jsonkin):

    def __init__(self,
        n_step: int,
        position: Point3D,
        bnstate: dict,
        light_values: list,
        distance_values: list,
        bumps_values: list):

        self.n_step = n_step
        self.bnstate = bnstate
        self.position = position
        self.light_values = light_values
        self.distance_values = distance_values
        self.bumps_values = bumps_values
        
    def to_json(self) -> dict:
        return {
            'n_step':self.n_step,
            'position':self.position.to_json(),
            'bnstate':self.bnstate,
            'light_values':self.light_values,
            'distance_values':self.distance_values,
            'bumps_values':self.bumps_values,
        }
    
    @staticmethod
    def from_json(json:dict):
        return SimulationStepData(
            json['n_step'],
            Point3D.from_json(json['position']),
            json['bnstate'],
            json['light_values'],
            json['distance_values'],
            json['bumps_values']
        )

#######################################################################

class BNParams(object):
    '''
    Container for BN generation parameters
    '''
    def __init__(self, N, K, P, I, O):
        
        self.N = N
        self.K = K
        self.P = P
        self.I = I
        self.O = O
    
    def __iter__(self):
        for i in vars(self).values():
            yield i

class ArenaParams(object):
    '''
    Container for Webots Arena options
    '''
    def __init__(self, 
            floor_size=(3, 3), 
            sim_config=Path('.'),
            controller='void'):
        
        self.floor_size = floor_size
        self.sim_config = sim_config
        self.controller = controller
    
        