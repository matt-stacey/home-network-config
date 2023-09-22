import yaml

from pathlib import Path


class YamlFile:
    def __init__(self, yaml_path: Path):
        self.yaml_path: Path = yaml_path
        self._data = None  # type: ignore

    def _load_data(self):
        with self.yaml_path.open('r') as f:
            self._data = yaml.safe_load(f.read())

    @property
    def data(self):
        if self._data is None:
            self._load_data()
        return self._data
