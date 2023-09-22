import os
import logging
import argparse

from time import perf_counter
from typing import List
from pathlib import Path

from data import Paths, Defaults
from logger import Logger
from yaml_handler import YamlFile
from configurer import ContainerConfigurer
# TODO combine into ContainerMaster, place here; pull in yaml handling/logging


# TODO remove logging here, use master
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


class ContainerMaster(Logger):
    def __init__(self, yaml_path: Path, sls_template_dir: str):
        super().__init__('container_master')
        self.container_roster: YamlFile = YamlFile(yaml_path)
        self.desired_containers = self.container_roster.data

    def copy_from(self, source_container: str) -> List[str]:
        if source_container not in self.current_containers:
            raise RuntimeError(f'Source container {source_container} does not exist!')

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

    @property
    def current_containers(self) -> List[str]:
        lxc_cmd: str = 'lxc-ls -f'
        lxc_output = os.popen(lxc_cmd)  # type: ignore
        lxc_data: List[str] = lxc_output.read().split('\n')[1:]
        containers: List[str] = [cont_info.split(' ')[0] for cont_info in lxc_data if len(cont_info) > 0]
        return containers


if __name__ == '__main__':
    parser = make_parser()
    args = parser.parse_args()

    containter_master = ContainerMaster(Path(args.yaml), Paths.sls_template_dir)

    containter_master.logger.info(containter_master.current_containers)
    containter_master.logger.info(containter_master.desired_containers.keys())

    container_roster = YamlFile(Path(args.yaml))
    configurer = ContainerConfigurer(container_roster, Paths.sls_template_dir)

    # TODO add arg to put in source container
    # TODO create MESG to copy in args
    created = []
    try:
        created = containter_master.copy_from(Defaults.source_container)
    except RuntimeError as err:
        containter_master.logger.warning(err)
    containter_master.logger.info(f'Created containers: {created}')

    containter_master.logger.info(configurer.sls_templates.keys())
    # TODO configure MESG in args

    # TODO turn them on (parser arg?)

    # TODO? output commands to attach
