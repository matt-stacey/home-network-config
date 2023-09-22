import glob
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from data import Paths
from logger import Logger
from yaml_handler import YamlFile


class ContainerConfigurer(Logger):
    def __init__(self, container_roster: YamlFile, sls_template_dir: str):
        super().__init__('configurer')

        self.container_roster: YamlFile = container_roster
        self.desired_containers = self.container_roster.data

        self.sls_template_dir: str  = sls_template_dir
        self.load_sls_templates()

    def load_sls_templates(self):
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_template_dir))
        self.sls_templates_path: Path = Paths.containerization / self.sls_template_dir

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

    # TODO function to 'mount' drives
    # from yaml data
    # .ssh

    # TODO function to create Git folder

    # TODO function to place (completed) templates

    # TODO configure as salt minion
