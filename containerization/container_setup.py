import glob
import yaml
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


from paths import Paths
from creator import ContainerCreator
from configurer import ContainerConfigurer


def make_parser():
    parser = argparse.ArgumentParser(description='Container Creator/Configurer')

    parser.add_argument('-Y', '--yaml',
                        required=True,
                        help='YAML with container data')

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    creator = ContainerCreator()
    configurer = ContainerConfigurer(args.yaml, Paths.sls_template_dir)

    print(configurer.containers)
    print(configurer.sls_templates.keys())


if __name__ == '__main__':
    main()
