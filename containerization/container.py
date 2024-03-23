import os
import socket
import subprocess

from time import perf_counter
from pathlib import Path

from data import Paths, Defaults
from logger import Logger


class Container(Logger):
    sls_template_dir: str = Paths.sls_template_dir

    def __init__(self, name: str, container_data):  # type: ignore
        super().__init__(name)

        self.name: str = f'{self.host}-{name}'  # include hostname in the name

        self.git_repos = []
        if Defaults.git_key in container_data:
            self.git_repos = list(container_data[Defaults.git_key])

    def __repr__(self):
        return self.name

    # Main functions
    def copy(self, source_container: str) -> bool:
        copy_cmd: str = 'lxc-copy -n {source_container} -N {self.name}'

        self.logger.info(f'Copying from {source_container}')
        output, time_taken = self.time_it(os.popen, copy_cmd)  # FIXME os

        if len(output.read()) == 0:
            # FIXME very weak way of determining if successful,
            #       but haven't encountered failing to see what that looks like yet
            self.logger.info(f'Copied in {time_taken} seconds')
            return True

        self.logger.warning(f'Copying failed after {time_taken} seconds')
        return False

    def remove(self) -> bool:
        remove_cmd: str = f'lxc-destroy -n {self.name}'

        self.logger.info('Removing')
        output, time_taken = self.time_it(os.popen, remove_cmd)  # FIXME os

        if len(output.read()) == 0:
            # FIXME very weak way of determining if successful,
            #       but haven't encountered failing to see what that looks like yet
            self.logger.info(f'Removed in {time_taken} seconds')
            return True

        self.logger.warning(f'Removing failed after {time_taken} seconds')
        return False

    def configure(self) -> bool:
        self.logger.info('Configuring')
        success: bool = True
        _, sls_load_time = self.time_it(self.load_sls_templates)

        _, git_time = self.time_it(self.clone_git_repos)

        # TODO other configuration

        cumulative_time = sls_load_time + \
                          git_time
        if success:
            self.logger.info(f'Configured in {cumulative_time} seconds')
        else:
            self.logger.warning(f'Configuring failed after {cumulative_time} seconds')
        return success

    def activate(self, turn_on: bool) -> bool:
        subcommand: str = 'start' if turn_on else 'stop'
        activate_cmd: str = f'lxc-{subcommand} -n {self.name}'

        self.logger.info(f'{subcommand.capitalize()}ing')
        output, time_taken = self.time_it(os.popen, activate_cmd)  # FIXME os

        if len(output.read()) == 0:
            # FIXME very weak way of determining if successful,
            #       but haven't encountered failing to see what that looks like yet
            self.logger.info(f'{subcommand.capitalize()}ed in {time_taken} seconds')
            return True

        self.logger.warning(f'{subcommand.capitalize()}ing failed after {time_taken} seconds')
        return False

    # Helper functions
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

    def clone_git_repos(self):
        git_directory: Path = self.user_home / 'git'
        subprocess.run(['lxc-attach', '-n', self.name, '--', 'mkdir', '~/git'])

        for repo in self.git_repos:
            clone_cmd: list[str] = ['lxc-attach', '-n', self.name,
                                    '--',
                                    'cd', '~/git'
                                    '&&',
                                    'git', 'clone', repo]
            subprocess.run(clone_cmd)

    # TODO function to place (completed) templates

    def minionize(self):
        # TODO configure as salt minion
        # create pillar/salt data
        pass

    # Properties
    @property
    def host(self) -> str:
        return socket.gethostname()

    @property
    def path(self) -> Path:
        return Paths.lxc_data / self.name

    @property
    def root(self) -> Path:
        return self.path / 'rootfs'  # TBD if all containers or just ubuntu

    @property
    def home(self) -> Path:
        return self.root / 'home'

    @staticmethod
    def time_it(func, *args, **kwargs):
        t_start: float = perf_counter()
        result = func(*args, **kwargs)
        t_stop: float = perf_counter()

        time_taken = t_stop - t_start
        return result, time_taken
