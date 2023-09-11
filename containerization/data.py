from pathlib import Path


class Paths:
    sls_template_dir: str = 'templates/'  # trailing slash for Jinja2
    sls_template_suffix: str = '.template'

class Defaults:
    source_container: str = 'x553-minion-bootstrapper'
