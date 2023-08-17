import os
import yaml
from pathlib import Path


class ContainerCreator:
    def __init__(self, roster_path: Path):
        self.container_roster: Path = roster_path
        self.load_roster()

    def load_roster(self):
        with self.container_roster.open('r') as f:
            self.desired_containers = yaml.safe_load(f.read())

    @property
    def current_containers(self) -> list[str]:
        lxc_cmd: str = 'lxc-ls -f'
        lxc_output = os.popen(lxc_cmd)  # type: ignore
        lxc_data: list[str] = lxc_output.read().split('\n')[1:]
        containers: list[str] = [cont_info.split(' ')[0] for cont_info in lxc_data if len(cont_info) > 0]
        return containers

