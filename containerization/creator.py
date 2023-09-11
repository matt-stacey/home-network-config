import os
import yaml
import logging
from time import perf_counter
from pathlib import Path


class ContainerCreator:
    def __init__(self, roster_path: Path):
        self.container_roster: Path = roster_path

        self.logger = logging.getLogger('creator')
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')  # type: ignore
        self.stream_handler = logging.StreamHandler()  # type: ignore
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

        self.load_roster()

    def load_roster(self):
        with self.container_roster.open('r') as f:
            self.desired_containers = yaml.safe_load(f.read())

    def create_from(self, source_container: str) -> list[str]:
        if source_container not in self.current_containers:
            raise RuntimeError(f'Source container {source_container} does not exist!')

        containers_before_copy: list[str] = list(self.current_containers)
        created_containers: list[str] = []
        copy_cmd: str = 'lxc-copy -n {source_container} -N {new_container}'

        for new_container in self.desired_containers.keys():
            if new_container in containers_before_copy:
                print(f'{new_container} already exists; skipping!')
                continue

            t_start: float = perf_counter()
            print(f'Copying {source_container} to {new_container}')
            result = os.popen(copy_cmd.format(source_container=source_container,
                                              new_container=new_container))
            if len(result.read()) == 0:  # FIXME very weak, but dunno what failing looks like yet
                created_containers.append(new_container)
            t_stop: float = perf_counter()
            print(f'    Copied {new_container} in {t_stop-t_start} seconds')

        return sorted(created_containers)

    @property
    def current_containers(self) -> list[str]:
        lxc_cmd: str = 'lxc-ls -f'
        lxc_output = os.popen(lxc_cmd)  # type: ignore
        lxc_data: list[str] = lxc_output.read().split('\n')[1:]
        containers: list[str] = [cont_info.split(' ')[0] for cont_info in lxc_data if len(cont_info) > 0]
        return containers

