import logging
import argparse

from pathlib import Path

from container_master import ContainerMaster

from data import Defaults
from logger import Logger


def make_parser():
    parser = argparse.ArgumentParser(description='Container Creator/Configurer')

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--copy', action='store_true', dest='copy', default=False)
    mode_group.add_argument('--configure', action='store_true', dest='configure', default=False)
    mode_group.add_argument('--activate', action='store_true', dest='activate', default=False)
    mode_group.add_argument('--deactivate', action='store_true', dest='deactivate', default=False)
    mode_group.add_argument('--start-salt', action='store_true', dest='start_salt', default=False)

    parser.add_argument('-C', '--source-container',
                             required=False,
                             default=Defaults.source_container,
                             help=f'Container from which to copy (default: {Defaults.source_container})')

    parser.add_argument('-Y', '--yaml',
                        required=True,
                        help='YAML with container data')

    return parser


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    container_master = ContainerMaster(Path(args.yaml))

    container_setup = Logger('container_setup')
    logger = container_setup.logger  # janky
    logger.setLevel(logging.DEBUG)
    logger.info(container_master.current_containers)

    if args.copy:
        logger.info(f'Copying containers from {args.source_container}')
        logger.debug(container_master.desired_containers.keys())
        created = container_master.copy_from(args.source_container)
        logger.info(f'Created containers: {created}')

    elif args.configure:
        logger.info('Configuring containers')
        logger.debug(container_master.sls_templates.keys())
        configured = container_master.configure()
        logger.info(f'Configured containers: {configured}')

    elif args.activate:
        logger.info('Activating containers')
        activated = container_master.activate_containers(True)
        logger.info(f'Activated containers: {activated}')

        # Show the user how to get into each container
        logger.info('To attach to a container, run:')
        for container in activated:
            logger.info(f'lxc-attach -n {container}')

    elif args.deactivate:
        logger.info('Dectivating containers')
        deactivated = container_master.activate_containers(False)
        logger.info(f'Deactivated containers: {deactivated}')

    elif args.start_salt:
        logger.info('Starting Salt on all containers')
        salted = container_master.start_salt_containers(False)
        logger.info(f'Salt started on containers: {salted}')

    else:
        logger.info('No action given!')
