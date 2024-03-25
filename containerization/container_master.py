import os

from time import perf_counter
from typing import List
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from logger import Logger
from yaml_handler import YamlFile

from container import Container


class ContainerMaster(Logger):
    def __init__(self, yaml_path: Path):
        super().__init__('container_master')

        self.managed_containers: List[Container] = self.create_container_roster(yaml_path)

    # Major functions
    def copy_from(self, source_container: str) -> List[str]:
        """
        Copy an LXC container to our new container names
        params: source_container: str
        return: created_containers: List[str]
        """
        created_containers: List[str] = []

        if source_container not in self.current_containers:
            self.log_and_raise(f'Source container {source_container} does not exist!')

        containers_before_copy: List[str] = list(self.current_containers)
        os.popen(f'lxc-stop -n {source_container}').read()  # Must be stopped before copying

        for new_container in self.managed_containers:
            if new_container.name in containers_before_copy:
                self.logger.warning(f'{new_container} already exists; skipping!')
                continue

            if new_container.copy(source_container):
                created_containers.append(new_container.name)

        return sorted(created_containers)

    def destroy(self) -> List[str]:
        """
        Destroy containers named in the YAML
        params: none
        return: destroyed_containers: List[str]
        """
        destroyed_containers: List[str] = []

        containers_before_destroy: List[str] = list(self.current_containers)

        for container in self.managed_containers:
            if container.name not in containers_before_destroy:
                self.logger.warning(f'{container} does not exist; skipping!')
                continue

            if container.remove():
                destroyed_containers.append(container.name)

        return sorted(destroyed_containers)

    def configure(self) -> List[str]:
        """
        Configure our containers
        params: none
        return: configured_containers: List[str]
        """
        configured_containers: List[str] = []

        for container in self.managed_containers:
            if container.name not in self.current_containers:
                self.logger.warning(f'Directed to configure {container}, but it couldn\'t be found!')
                continue

            if container.configure():
                configured_containers.append(container.name)

        return sorted(configured_containers)

    def activate_containers(self, turn_on: bool) -> List[str]:
        """
        Activate or deactivate our containers
        params: turn_on: bool
        return: activated_containers: List[str]
        """
        activated_containers: List[str] = []
        subcommand: str = 'start' if turn_on else 'stop'

        for container in self.managed_containers:
            if container.name not in self.current_containers:
                self.warn_and_continue(f'Container {container} does not exist; cannot {subcommand} it!')
                continue

            if container.activate(turn_on):
                activated_containers.append(container.name)

        return sorted(activated_containers)

    def start_salt_containers(self, input_var):
        """
        TODO doc string and function, or remove from setup script
        """
        return input_var

    # Helper functions
    def create_container_roster(self, yaml_path: Path) -> List[Container]:
        self._container_yaml: YamlFile = YamlFile(yaml_path)
        managed_containers: List[Container] = [Container(container_name, self._container_yaml.data[container_name])
                                               for container_name in self._container_yaml.data.keys()]
        return managed_containers

    @property
    def current_containers(self) -> List[str]:
        lxc_cmd: str = 'lxc-ls -f'
        lxc_output = os.popen(lxc_cmd)  # type: ignore
        lxc_data: List[str] = lxc_output.read().split('\n')[1:]
        containers: List[str] = [cont_info.split(' ')[0] for cont_info in lxc_data if len(cont_info) > 0]
        return containers
