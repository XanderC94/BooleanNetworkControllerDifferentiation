from bncontroller.json_utils import Jsonkin
import json, random, math
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

    def to_json(self) -> dict:
        return vars(self)

    @staticmethod
    def from_json(json:dict):
        return Point3D(
            json['x'],
            json['y'],
            json['z']
        )

    @staticmethod
    def from_tuple(coordinates: list or (float, float, float)):
        return Point3D(coordinates[0], coordinates[1], coordinates[2])

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

if __name__ == "__main__":
    
    data = defaultdict(list)
    p = Point3D(0.0,0.0,0.0)

    for i in range(10):

        p.x += 0.1
        p.z += 0.1

        print(p)

        data['data'].append(
            SimulationStepData(
                i, 
                Point3D(p.x, 0.0, p.z),
                [0.0 for _ in range(20)],
                [random.random() for _ in range(8)],
                [random.random() for _ in range(8)],
                [random.random() for _ in range(8)]
            )
        )

    from bncontroller.json_utils import write_json

    write_json(data, Path('./data.json'))