import os
import socket

from pathlib import Path


class Paths:
    repo: Path = Path(os.popen('git rev-parse --show-toplevel').read().strip())
    containerization: Path = repo / 'containerization'
    sls_template_dir: str = 'templates/'  # trailing slash for Jinja2
    sls_template_suffix: str = '.template'

    lxc_data: Path = Path('/var/lib/lxc/')

    logs_dir: Path = containerization / 'logs'

    @staticmethod
    def container_data(container):
        return Paths.lxc_data / container


class Data:
    hostname: str = socket.gethostname()
    source_container: str = f'{hostname}-minion_bootstrapper'

    # Keys from YAML config files
    git_key: str = 'git_urls'  # git repos to be cloned
    cmds_key: str = 'commands'  # commands to run
    mount_key: str = 'mount'  # mount points
