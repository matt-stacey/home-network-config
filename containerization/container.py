import os

from time import perf_counter

from data import Paths
from logger import Logger


class Container(Logger):
    sls_template_dir: str = Paths.sls_template_dir

    def __init__(self, name: str, container_data):  # type: ignore
        super().__init__(name)

        self.name: str = name

    def __repr__(self):
        return self.name

    # Main functions
    def copy(self, source_container: str) -> bool:
        copy_cmd: str = 'lxc-copy -n {source_container} -N {self.name}'

        self.logger.info(f'Copying from {source_container}')
        output, time_taken = self.time_it(os.popen, copy_cmd)

        if len(output.read()) == 0:
            # FIXME very weak way of determining if copied successfully,
            #       but haven't encountered failing to see what that looks like yet
            self.logger.info(f'Copied in {time_taken} seconds')
            return True

        self.logger.warning(f'Copying failed after {time_taken} seconds')
        return False

    def configure(self) -> bool:
        self.logger.info(f'Configuring')
        success: bool = True
        _, cumulative_time = self.time_it(self.load_sls_templates)

        # TODO other configuration

        if success:
            self.logger.info(f'Configured in {cumulative_time} seconds')
        else:
            self.logger.warning(f'Configuring failed after {cumulative_time} seconds')
        return success

    # Helper functions
    def load_sls_templates(self):
        self.sls_templates_path: Path = Paths.containerization / self.sls_template_dir
        self.sls_template_env = Environment(loader=FileSystemLoader(self.sls_templates_path))

        self.sls_templates = {}  # type: ignore

        for file_path in self.sls_templates_path.glob('*'):
            if file_path.suffix == Paths.sls_template_suffix:
                self.sls_templates[file_path.stem] = self.sls_template_env.get_template(file_path.name)

    @staticmethod
    def time_it(func, *args):
        t_start: float = perf_counter()
        result = func(*args)
        t_stop: float = perf_counter()

        time_taken = t_stop - t_start
        return result, time_taken
