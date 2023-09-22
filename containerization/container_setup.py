import logging
import argparse
from pathlib import Path

from data import Paths, Defaults
from yaml_handler import YamlFile
from creator import ContainerCreator
from configurer import ContainerConfigurer
# TODO combine into ContainerMaster, place here; pull in yaml handling/logging


logger = logging.getLogger('main')
logger.setLevel(logging.INFO)
FORMAT = '%(asctime)s: %(name)s: %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT)


def make_parser():
    parser = argparse.ArgumentParser(description='Container Creator/Configurer')

    parser.add_argument('-Y', '--yaml',
                        required=True,
                        help='YAML with container data')

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    container_roster = YamlFile(Path(args.yaml))
    creator = ContainerCreator(container_roster)
    configurer = ContainerConfigurer(container_roster, Paths.sls_template_dir)

    logger.info(creator.current_containers)
    logger.info(creator.desired_containers.keys())

    # TODO add arg to put in source container
    # TODO create MESG to copy in args
    created = creator.copy_from(Defaults.source_container)
    logger.info(f'Created containers: {created}')

    logger.info(configurer.sls_templates.keys())
    # TODO configure MESG in args

    # TODO turn them on (parser arg?)
    
    # TODO? output commands to attach


if __name__ == '__main__':
    main()  # TODO instance to run
