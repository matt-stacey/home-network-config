import yaml


class YamlFile:
    def __init__(self, yaml_path: Path):
        self.yaml_path: Path = yaml_path

        with self.yaml_path.open('r') as f:
            self._data = yaml.safe_load(f.read())

    @property
    def data(self):
        # TODO jit
        return self._data
