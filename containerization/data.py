import os
from pathlib import Path


class Paths:
    repo: Path = Path(os.popen('git rev-parse --show-toplevel').read().strip())
    containerization: Path = repo / 'containerization'
    sls_template_dir: str = 'templates/'  # trailing slash for Jinja2
    sls_template_suffix: str = '.template'

    logs_dir: Path = containerization / 'logs'

class Defaults:
    source_container: str = 'x553-minion-bootstrapper'
