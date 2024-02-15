import osy

from data import Paths
from logger import Logger


class Container(logger):
    sls_template_dir: str = Paths.sls_template_dir

    def __init__(self, name: str, container_data):  # type: ignore
        super().__init__(name)

        self.name: str = name

    def __repr__(self):
        return self.name

    # Main functions
    def copy(self, source_container: str) -> bool:
        copy_cmd: str = 'lxc-copy -n {source_container} -N {self.name}'
        output = os.popen(copy_cmd)

        if len(output.read()) == 0:
            # FIXME very weak way of determining if copied successfully,
            #       but haven't encountered failing to see what that looks like yet
            return True
        return False

    def configure(self):
        self.load_sls_templates()
        #other configuration

    # Helper functions
    def load_sls_templates(self):
        self.sls_templates_path: Path = Paths.containerization / self.sls_template_dir
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_templates_path))

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)
