import socket
import subprocess

from jinja2 import Environment, FileSystemLoader

from time import perf_counter
from pathlib import Path

from data import Paths, Data
from logger import Logger


class Container(Logger):
    sls_template_dir: str = Paths.sls_template_dir

    def __init__(self, name: str, container_data):  # type: ignore
        super().__init__(name)

        self.name: str = f'{self.host}-{name}'  # include hostname in the name
        self.container_data = container_data  # type: ignore

        self.git_repos: list[str] = self.load_list_from_config_yaml(Data.git_key)
        self.commands: dict[str, list[str]] = self.load_dict_from_config_yaml(Data.cmds_key)
        self.mount_points: dict[str, str] = self.load_dict_from_config_yaml(Data.mount_key)

    def __repr__(self):
        return self.name

    # Main functions
    def copy(self, source_container: str) -> bool:
        copy_cmd: str = f'lxc-copy -n {source_container} -N {self.name}'

        self.logger.info(copy_cmd)
        output, time_taken = self.time_run(copy_cmd.split(" "))

        if output.returncode == 0:
            self.logger.info(f'Copied in {time_taken} seconds')
            return True

        self.logger.warning(f'Copying failed after {time_taken} seconds with returncode {output.returncode}')
        return False

    def remove(self) -> bool:
        remove_cmd: str = f'lxc-destroy -n {self.name}'

        self.deactivate()
        self.logger.info(remove_cmd)
        output, time_taken = self.time_run(remove_cmd.split(" "))

        if output.returncode == 0:
            self.logger.info(f'Removed in {time_taken} seconds')
            return True

        self.logger.warning(f'Removing failed after {time_taken} seconds with returncode {output.returncode}')
        return False

    def configure_local(self) -> bool:
        self.logger.info('Beginning local configuration')
        success: bool = True
        _, sls_load_time = self.time_it(self.load_sls_templates)

        self.deactivate()
        _, mnt_time = self.time_it(self.set_mount_points)

        self.activate()
        _, cmd_time = self.time_it(self.execute_command_list, local=True)

        # TODO other configuration

        cumulative_time = sls_load_time + \
                          mnt_time + \
                          cmd_time

        if success:
            self.logger.info(f'Configured (local) in {cumulative_time} seconds')
        else:
            self.logger.warning(f'Configuring (local) failed after {cumulative_time} seconds')
        return success

    def configure_connected(self) -> bool:
        self.logger.info('Beginning networked configuration')
        success: bool = True

        self.activate()
        _, git_time = self.time_it(self.clone_git_repos)

        _, cmd_time = self.time_it(self.execute_command_list, local=False)

        # TODO other configuration

        cumulative_time = git_time + \
                          cmd_time

        if success:
            self.logger.info(f'Configured (connected) in {cumulative_time} seconds')
        else:
            self.logger.warning(f'Configuring (connected) failed after {cumulative_time} seconds')
        return success

    def activate(self, turn_on: bool=True) -> bool:
        subcommand: str = 'start' if turn_on else 'stop'
        activate_cmd: str = f'lxc-{subcommand} -n {self.name}'

        self.logger.info(activate_cmd)
        output, time_taken = self.time_run(activate_cmd.split(" "))

        if output.returncode == 0:
            self.logger.info(f'{subcommand.capitalize()}ed in {time_taken} seconds')
            return True

        self.logger.warning(f'{subcommand.capitalize()}ing failed after {time_taken} seconds with returncode {output.returncode}')
        return False

    def deactivate(self) -> bool:
        return self.activate(turn_on=False)

    # Helper functions - Timed with time_it
    def load_sls_templates(self):
        self.sls_templates_path: Path = Paths.containerization / self.sls_template_dir
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_templates_path))

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

    def clone_git_repos(self):
        git_path: Path = Path("/usr/bin/git")
        git_repo_dir: Path = Path("/root/git")
        create_git: str = self.attached_command(f"mkdir -p {git_repo_dir}")
        subprocess.run(create_git.split(" "))

        for repo in self.git_repos:
            repo_name: str = repo.split("/")[-1].split(".")[0]
            clone_cmd: str = self.attached_command(f"{git_path} clone {repo} {git_repo_dir}/{repo_name}")
            subprocess.run(clone_cmd.split(" "))

    def execute_command_list(self, local: bool=True):
        commands_key: str = "local" if local else "connected"
        for command in self.commands[commands_key]:
            cmd_to_run: str = self.attached_command(command)
            subprocess.run(cmd_to_run.split(" "))

    def set_mount_points(self):
        # each mount point needs added at
        # /var/lib/lxc/<container>/config with:
        # lxc.mount.entry = /root/.ssh srv/.ssh none bind 0 0

        for host_location, container_args in self.mount_points.items():
            if not Path(host_location).exists():
                self.logging.error(f"{host_location} does not exist on {self.host}")
                return
            container_mount_point: Path = self.root / container_args.split(" ")[0]
            if not container_mount_point.exists():
                container_mount_point.mkdir(parents=True, exist_ok=True)

        mount_note: list[str] = ["",
                                 "# Additional mount points"
                                ] + [f"lxc.mount.entry = {host_location} {container_args}"
                                     for host_location, container_args in self.mount_points.items()]

        # Idempotency check
        try:
            for mount_entry in mount_note[1:]:
                output = subprocess.check_output(["grep", mount_entry, self.config]) # type:  ignore
            self.logger.info("Mount points previously set")
            return
        except subprocess.CalledProcessError as e:
            # encountered if grep does not find any mount_entry
            pass

        for line in mount_note:
            config_line: str = subprocess.Popen(["echo", line], stdout=subprocess.PIPE)
            output = subprocess.check_output(["sudo", "tee", "-a", self.config], stdin=config_line.stdout)  # type: ignore
            config_line.wait()

    # TODO function to place (completed) templates

    def minionize(self):
        # TODO configure as salt minion
        # create pillar/salt data
        pass

    # Helper functions - Untimed
    def load_list_from_config_yaml(self, yaml_key:str):
        output = []
        if yaml_key in self.container_data and self.container_data[yaml_key]:
            output = list(self.container_data[yaml_key])
        return output

    def load_dict_from_config_yaml(self, yaml_key:str):
        output = {}
        if yaml_key in self.container_data and self.container_data[yaml_key]:
            output = dict(self.container_data[yaml_key])
        return output

    def attached_command(self, command:str) -> str:
        new_command: str = f"lxc-attach -n {self.name} -- {command}"
        self.logger.info(new_command)
        return new_command

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
    def root_home(self) -> Path:
        return self.root / "root"

    @property
    def root_git(self) -> Path:
        return self.root_home / "git"

    @property
    def home(self) -> Path:
        return self.root / 'home'

    # Process timing
    @staticmethod
    def time_it(func, *args, **kwargs):
        t_start: float = perf_counter()
        result = func(*args, **kwargs)
        t_stop: float = perf_counter()

        time_taken = t_stop - t_start
        return result, time_taken

    @staticmethod
    def time_run(command_list):
        t_start: float = perf_counter()
        result = subprocess.run(command_list)
        t_stop: float = perf_counter()

        time_taken = t_stop - t_start
        return result, time_taken

