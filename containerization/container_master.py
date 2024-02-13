import os

from time import perf_counter
from typing import List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from data import Paths
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
        
        for container in self.desired_containers:
            if container not in self.created_containers:
                self.logger.warning(f'Directed to configure {container}, but it couldn\'t be found!')
                continue
            
            

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

    def activate_containers(self, turn_on: bool):
        activated_containers: List[str] = []
        subcommand: str = 'start' if turn_on else 'stop'
        activate_cmd: str = 'lxc-{subcommand} -n {new_container}'

        for new_container in self.desired_containers.keys():
            if new_container not in self.current_containers:
                self.logger.warn_and_continue(f'Container {new_container} does not exist; cannot {subcommand} it!')
                continue

            t_start: float = perf_counter()
            self.logger.info(f'{subcommand.capitalize()}ing {new_container}')
            result = os.popen(activate_cmd.format(subcommand=subcommand,
                                                  new_container=new_container))
            if len(result.read()) == 0:  # FIXME very weak, but dunno what failing looks like yet
                activated_containers.append(new_container)
            t_stop: float = perf_counter()
            self.logger.info(f'{subcommand.capitalize()}ed {new_container} in {t_stop-t_start} seconds')

        return sorted(activated_containers)

    @property
    def current_containers(self) -> List[str]:
        lxc_cmd: str = 'lxc-ls -f'
        lxc_output = os.popen(lxc_cmd)  # type: ignore
        lxc_data: List[str] = lxc_output.read().split('\n')[1:]
        containers: List[str] = [cont_info.split(' ')[0] for cont_info in lxc_data if len(cont_info) > 0]
        return containers
