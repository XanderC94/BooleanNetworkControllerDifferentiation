from pathlib import Path
from argparse import ArgumentParser, Action
from bncontroller.sim.config import Config, CONFIG_CLI_NAMES

class AutoConfigParser(Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):

        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        
        setattr(namespace, self.dest, Config.from_file(values))

def parse_args(parser=ArgumentParser('Configuration Parse Unit.')):
    '''
    Parses Command Line Arguments, 
    returning:
        * parsed arguments as objects
        * unknown (unparsed) ones as list of strings
    '''
    parser.add_argument(
        *CONFIG_CLI_NAMES, 
        type=Path, 
        action=AutoConfigParser,
        help= 'Path to Configuration file.',
        dest='config',
        metavar='/path/to/config.json'
    )

    # args = parser.parse_args()
    args, unknown = parser.parse_known_args()

    return args, unknown
    