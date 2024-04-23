import logging
import argparse

from pathlib import Path

from container_master import ContainerMaster

from data import Data
from logger import Logger


def make_parser():
    parser = argparse.ArgumentParser(description='Container Creator/Configurer')

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--copy', action='store_true', dest='copy', default=False)
    mode_group.add_argument('--destroy', action='store_true', dest='destroy', default=False)
    mode_group.add_argument('--configure-local', action='store_true', dest='configure_local', default=False)
    mode_group.add_argument('--configure-connected', action='store_true', dest='configure_connected', default=False)
    mode_group.add_argument('--activate', action='store_true', dest='activate', default=False)
    mode_group.add_argument('--deactivate', action='store_true', dest='deactivate', default=False)
    mode_group.add_argument('--start-salt', action='store_true', dest='start_salt', default=False)

    parser.add_argument('-C', '--source-container',
                             required=False,
                             default=Data.source_container,
                             help=f'Container from which to copy (default: {Data.source_container})')

    parser.add_argument('-Y', '--yaml',
                        required=True,
                        help='YAML with container data')

    return parser


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    container_setup = Logger('container_setup')
    logger = container_setup.logger  # janky
    logger.setLevel(logging.DEBUG)

    container_master = ContainerMaster(Path(args.yaml))
    logger.info(f'Existing containers: {container_master.current_containers}')
    if len(container_master.managed_containers) < 1:
        logger.log_and_raise(f"No containers to manage! {container_master.managed_containers}")

    if args.copy:
        logger.info(f'Copying containers from {args.source_container}')
        logger.debug(container_master.managed_containers)
        created = container_master.copy_from(args.source_container)
        logger.info(f'Created containers: {created}')

    elif args.destroy:
        logger.info('Destroying containers')
        destroyed = container_master.destroy()
        logger.info(f'Destroyed containers: {destroyed}')

    elif args.configure_local:
        logger.info('Configuring containers with local data')
        configured = container_master.configure(local=True)
        logger.info(f'Configured (local) containers: {configured}')
        logger.info('Activate containters with --activate and ensure they have IP addresses before continuing')

    elif args.configure_connected:
        logger.info('Configuring containers with non-local data')
        configured = container_master.configure(local=False)
        logger.info(f'Configured (non-local) containers: {configured}')
        logger.info('Activate containters with --activate and ensure they have IP addresses before continuing')

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

    logger.info(f'Existing containers: {container_master.current_containers}')

