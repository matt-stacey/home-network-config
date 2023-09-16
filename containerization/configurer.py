import glob
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from data import Paths
from logger import Logger


class ContainerConfigurer(Logger):
    def __init__(self, sls_template_dir: str):
        super().__init__('configurer')

        self.sls_template_dir: str  = sls_template_dir
        self.load_sls_templates()

    def load_sls_templates(self):
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_template_dir))
        self.sls_templates_path: Path = Path(self.sls_template_dir)

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

