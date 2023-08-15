import glob
import yaml
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class Paths:
    sls_template_dir: str = 'templates/'  # trailing slash for Jinja2
    sls_template_suffix: str = '.template'


class ContainerCreator:
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


def make_parser():
    parser = argparse.ArgumentParser(description='Container Creator/Configurer')

    parser.add_argument('-Y', '--yaml',
                        required=True,
                        help='YAML with container data')

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    container_creator = ContainerCreator(args.yaml, Paths.sls_template_dir)

    print(container_creator.containers)
    print(container_creator.sls_templates.keys())


if __name__ == '__main__':
    main()
