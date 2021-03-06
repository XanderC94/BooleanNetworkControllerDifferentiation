import re
import subprocess
import shutil
from pathlib import Path
from bncontroller.sim.config import CONFIG_CLI_NAMES
from bncontroller.sim.utils import GLOBALS
from bncontroller.filelib.utils import check_path, FROZEN_DATE
from bncontroller.jsonlib.utils import read_json, write_json
from bncontroller.sim.config import Config
from bncontroller.sim.data import ArenaParams
from bncontroller.boolnet.structures import OpenBooleanNetwork
from bncontroller.filelib.utils import get_dir

def generate_webots_worldfile(template_path: Path, target_path: Path, world_params: ArenaParams):

    if template_path.is_dir() or target_path.is_dir():
        raise Exception('Simuation world path is not a file.') 

    check_path(target_path.parent, create_if_dir=True)

    TEMPLATE = r'\s*controllerArgs\s\"(?:{names})=\\\"(.*)\\\"\"\n'

    controller_args_pattern = TEMPLATE.format(names='|'.join(CONFIG_CLI_NAMES))
    floorsize_pattern = r'\s*floorSize\s+(\d+\s\d+)\n'
    floorradius_pattern = r'\s*radius\s+(\d+)\n'
    controller_pattern = r'\s*controller\s+\"(\w*)\"\n'
    
    controller_args_sub_value = str(world_params.sim_config).replace('\\', '/')
    
    size = world_params.floor_size

    if isinstance(size, float):
        floorradius_sub_value = str(size).replace(',', '')
        floorsize_sub_value = str((size, size))[1:-1].replace(',', '')
    else:
        floorradius_sub_value = str(size[0]).replace(',', '')
        floorsize_sub_value = str(size)[1:-1].replace(',', '')

    controller_sub_value = world_params.controller

    text = []

    def sub(x: re.Match, s: str):
        return ''.join([x.string[:x.start(1)], s, x.string[x.end(1):]])

    with open(template_path, 'r') as temp:

        text = temp.readlines()

        epuck_found = False

        for i, line in enumerate(text):

            if "robot" in line.lower():
                epuck_found = False

            if "e-puck" in line.lower():
                epuck_found = True
            
            text[i] = re.sub(
                controller_args_pattern, 
                lambda x: sub(x, controller_args_sub_value), 
                line
            )

            if hash(text[i]) == hash(line):
                text[i] = re.sub(
                    floorsize_pattern, 
                    lambda x: sub(x, floorsize_sub_value), 
                    line
                )

            if hash(text[i]) == hash(line):
                text[i] = re.sub(
                    floorradius_pattern, 
                    lambda x: sub(x, floorradius_sub_value), 
                    line
                )

            if hash(text[i]) == hash(line) and epuck_found:
                text[i] = re.sub(
                    controller_pattern, 
                    lambda x: sub(x, controller_sub_value), 
                    line
                )

    with open(target_path, 'w') as tar:
        tar.write(''.join(text))

def generate_webots_props_path(template_path: Path):

    return template_path.parent / '.{name}.wbproj'.format(
        name=template_path.with_suffix('').name
    )

def generate_webots_props_file(template_path: Path, target_path: Path):

    template_props_path = generate_webots_props_path(template_path)
    target_props_path = generate_webots_props_path(target_path)

    if template_props_path.is_file():

        target_props_path.write_text(
            template_props_path.read_text()
        )    

        return template_props_path, target_props_path
    else:
        return False
    
#####################################################################################

def run_simulation(config: Config, bn: OpenBooleanNetwork) -> dict:

    # Save model (inside or outside of the config? mumble rumble)
    write_json(bn.to_json(), config.bn_model_path) # BN Model
    write_json(config.to_json(), config.sim_config_path, indent=True) # Simulation Configuration

    # Run Webots    
    proc_closure = subprocess.run([
        str(config.webots_path), *config.webots_launch_opts, str(config.webots_world_path)
    ])

    return proc_closure

#####################################################################################

def save_subopt_model(path: Path, score: object, it: int, bn: dict, save_subopt=False):
        
    bn.update({'stats': dict(score=score, it=it)})

    model_dir = get_dir(path)

    if save_subopt: 
        # Save only if <sd_save_suboptimal_models> >= score
        write_json(bn, model_dir / GLOBALS.app['subopt_model_name'].format(
            date=FROZEN_DATE,
            it=GLOBALS.app['it_suffix'].format(it=it)
        ))
        
    # Always save the last suboptimal model (overwrite)
    write_json(bn, model_dir / GLOBALS.app['last_model_name'].format(
        date=FROZEN_DATE
    ))

########################################################################################

def clean_generated_worlds(template_world: Path):
    parts = template_world.with_suffix('').name.split('.')
    for p in template_world.parent.iterdir():
        if not any(part in p.name for part in parts) and ('wbt' in p.suffix or 'wbproj' in p.suffix):
            # print(p)
            p.unlink()


def clean_dir(path: Path):
    if Path(path).is_dir():
        shutil.rmtree(path)

def clean_tmpdir():
    clean_dir(path=Path('./tmp/'))

###################################################################
