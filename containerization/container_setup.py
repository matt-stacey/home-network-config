import os
import argparse

from time import perf_counter
from typing import List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from data import Paths, Defaults
from logger import Logger
from yaml_handler import YamlFile


class ContainerMaster(Logger):
    def __init__(self, yaml_path: Path):
        super().__init__('container_master')

        self.container_roster: YamlFile = YamlFile(yaml_path)
        self.desired_containers = self.container_roster.data

        self.sls_template_dir: str = Paths.sls_template_dir

    def copy_from(self, source_container: str) -> List[str]:
        if source_container not in self.current_containers:
            self.logger.log_and_raise(f'Source container {source_container} does not exist!')

        containers_before_copy: List[str] = list(self.current_containers)
        created_containers: List[str] = []
        copy_cmd: str = 'lxc-copy -n {source_container} -N {new_container}'

        for new_container in self.desired_containers.keys():
            if new_container in containers_before_copy:
                self.logger.warning(f'{new_container} already exists; skipping!')
                continue

            t_start: float = perf_counter()
            self.logger.info(f'Copying {source_container} to {new_container}')
            result = os.popen(copy_cmd.format(source_container=source_container,
                                              new_container=new_container))
            if len(result.read()) == 0:  # FIXME very weak, but dunno what failing looks like yet
                created_containers.append(new_container)
            t_stop: float = perf_counter()
            self.logger.info(f'Copied {new_container} in {t_stop-t_start} seconds')

        return sorted(created_containers)

    def configure(self):
        self.load_sls_templates()

    def load_sls_templates(self):
        self.sls_templates_path: Path = Paths.containerization / self.sls_template_dir
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_templates_path))

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

    # TODO function to 'mount' drives
    # from yaml data
    # .ssh

    # TODO function to create Git folder

    # TODO function to place (completed) templates

    def minionize(self):
        # TODO configure as salt minion
        # create pillar/salt data
        pass

    def activate_containers(self):
        activated_containers: List[str] = []
        activate_cmd: str = 'lxc-start -n {new_container}'

        for new_container in self.desired_containers.keys():
            if new_container not in self.current_containers:
                self.logger.warn_and_continue(f'Container {source_container} does not exist; cannot start it!')
                continue

            t_start: float = perf_counter()
            self.logger.info(f'Starting {new_container}')
            result = os.popen(copy_cmd.format(new_container=new_container))
            if len(result.read()) == 0:  # FIXME very weak, but dunno what failing looks like yet
                activated_containers.append(new_container)
            t_stop: float = perf_counter()
            self.logger.info(f'Started {new_container} in {t_stop-t_start} seconds')

        return sorted(activated_containers)

    def deactivate_containers(self):  # TODO
        pass

    @property
    def current_containers(self) -> List[str]:
        lxc_cmd: str = 'lxc-ls -f'
        lxc_output = os.popen(lxc_cmd)  # type: ignore
        lxc_data: List[str] = lxc_output.read().split('\n')[1:]
        containers: List[str] = [cont_info.split(' ')[0] for cont_info in lxc_data if len(cont_info) > 0]
        return containers


def make_parser():
    parser = argparse.ArgumentParser(description='Container Creator/Configurer')

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--copy', action='store_true', dest='copy', default=False)
    mode_group.add_argument('--configure', action='store_true', dest='configure', default=False)
    mode_group.add_argument('--activate', action='store_true', dest='activate', default=False)
    mode_group.add_argument('--deactivate', action='store_true', dest='deactivate', default=False)

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

    container_master.logger.info(container_master.current_containers)

    if args.copy:
        container_master.logger.info(f'Copying containers from {args.source_container}')
        container_master.logger.info(container_master.desired_containers.keys())

        created = []  # FIXME remove
        try:  # FIXME remove
            created = container_master.copy_from(args.source_container)
        except RuntimeError as err:  # FIXME remove
            container_master.logger.warning(err)  # FIXME remove
        container_master.logger.info(f'Created containers: {created}')

    elif args.configure:
        container_master.logger.info('Configuring containers')
        container_master.logger.info(container_master.sls_templates.keys())
        container_master.configure()

    elif args.activate:
        container_master.logger.info('Activating containers')
        activated = container_master.activate_containers()
        container_master.logger.info(f'Created containers: {activated}')
        # TODO? output commands to attach

    elif args.deactivate:
        container_master.logger.info('Dectivating containers')
        container_master.deactivate_containers()

    else:
        container_master.logger.info('No action given!')
