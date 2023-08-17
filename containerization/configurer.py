import glob
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


from paths import Paths


class ContainerConfigurer:
    def __init__(self, roster_file: str, sls_template_dir: str):
        self.container_roster: Path = Path(roster_file)
        self.load_roster()

        self.sls_template_dir: str  = sls_template_dir
        self.load_sls_templates()

    def load_roster(self):
        with self.container_roster.open('r') as f:
            self.containers = yaml.safe_load(f.read())

    def load_sls_templates(self):
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_template_dir))
        self.sls_templates_path: Path = Path(self.sls_template_dir)

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

