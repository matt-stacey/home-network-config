import glob
import yaml
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


from data import Paths


class ContainerConfigurer:
    def __init__(self, sls_template_dir: str):
        self.sls_template_dir: str  = sls_template_dir

        self.logger = logging.getLogger('configurer')
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')  # type: ignore
        self.stream_handler = logging.StreamHandler()  # type: ignore
        self.stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.stream_handler)

        self.load_sls_templates()

    def load_sls_templates(self):
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_template_dir))
        self.sls_templates_path: Path = Path(self.sls_template_dir)

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

