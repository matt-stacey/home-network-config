import os
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

class Defaults:
    source_container: str = 'z97x-minion_bootstrapper'

    git_key: str = 'git_urls'  # key in YAML to indicate a git repo to be cloned
    cmds_key: str = 'commands'  # key to indicate a list of commands to run
