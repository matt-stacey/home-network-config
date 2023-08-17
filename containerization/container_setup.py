import argparse
from pathlib import Path


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

    creator = ContainerCreator(Path(args.yaml))
    configurer = ContainerConfigurer(Paths.sls_template_dir)

    print(creator.current_containers)
    print(creator.desired_containers.keys())

    print(configurer.sls_templates.keys())


if __name__ == '__main__':
    main()
