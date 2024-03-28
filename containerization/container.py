import os
import socket
import subprocess

from time import perf_counter
from pathlib import Path

from data import Paths, Data
from logger import Logger


class Container(Logger):
    sls_template_dir: str = Paths.sls_template_dir

    def __init__(self, name: str, container_data):  # type: ignore
        super().__init__(name)

        self.name: str = f'{self.host}-{name}'  # include hostname in the name

        self.git_repos: list[str] = []
        if Data.git_key in container_data and container_data[Data.git_key]:
            self.git_repos = list(container_data[Data.git_key])

        self.commands: list[str] = []
        if Data.cmds_key in container_data and container_data[Data.cmds_key]:
            self.commands = list(container_data[Data.cmds_key])

        self.mount_points: list[str] = []
        if Data.mount_key in container_data and container_data[Data.mount_key]:
            self.mount_points = list(container_data[Data.mount_key])

    def __repr__(self):
        return self.name

    # Main functions
    def copy(self, source_container: str) -> bool:
        copy_cmd: str = f'lxc-copy -n {source_container} -N {self.name}'

        self.logger.info(copy_cmd)
        output, time_taken = self.time_popen(copy_cmd)  # FIXME os

        if len(output) == 0:
            # FIXME very weak way of determining if successful,
            #       but haven't encountered failing to see what that looks like yet
            self.logger.info(f'Copied in {time_taken} seconds')
            return True

        self.logger.warning(f'Copying failed after {time_taken} seconds')
        return False

    def remove(self) -> bool:
        remove_cmd: str = f'lxc-destroy -n {self.name}'

        self.logger.info(remove_cmd)
        output, time_taken = self.time_popen(remove_cmd)  # FIXME os

        if len(output) == 0:
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
        _, cmd_time = self.time_it(self.execute_command_list)
        _, mnt_time = self.time_it(self.set_mount_points)

        # TODO other configuration

        cumulative_time = sls_load_time + \
                          git_time + \
                          cmd_time + \
                          mnt_time
        if success:
            self.logger.info(f'Configured in {cumulative_time} seconds')
        else:
            self.logger.warning(f'Configuring failed after {cumulative_time} seconds')
        return success

    def activate(self, turn_on: bool) -> bool:
        subcommand: str = 'start' if turn_on else 'stop'
        activate_cmd: str = f'lxc-{subcommand} -n {self.name}'

        self.logger.info(activate_cmd)
        output, time_taken = self.time_popen(activate_cmd)  # FIXME os

        if len(output) == 0:
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

    def execute_command_list(self):
        for command in self.commands:
            cmd_to_run: list[str] = ['lxc-attach', '-n', self.name,
                                      '--', command]
            subprocess.run(cmd_to_run)

    def set_mount_points(self):
        # each mount point needs added at
        # /var/lib/lxc/<container>/config with:
        # lxc.mount.entry = /root/.ssh srv/.ssh none bind 0 0
        mount_note: list[str] = ["",
                                 "# Additional mount points"
                                ]

        for line in mount_note + self.mount_points:
            command: list[str] = ["echo", line, ">>", f"{self.config}"]
            subprocess.run(command)

    # TODO function to place (completed) templates

    def minionize(self):
        # TODO configure as salt minion
        # create pillar/salt data
        pass

    # Properties
    @property
    def host(self) -> str:
        return Data.hostname

    @property
    def path(self) -> Path:
        return Paths.lxc_data / self.name

    @property
    def config(self) -> Path:
        return self.path / 'config'

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

    @staticmethod
    def time_popen(command):
        t_start: float = perf_counter()
        result = os.popen(command).read()
        t_stop: float = perf_counter()

        time_taken = t_stop - t_start
        return result, time_taken
