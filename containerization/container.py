import osy

from logger import Logger


class Container(logger):
    def __init__(self, name: str, container_data):  # type: ignore
        super().__init__(name)

        self.name: str = name

    def __repr__(self):
        return self.name

    def copy(self, source_container: str) -> bool:
        copy_cmd: str = 'lxc-copy -n {source_container} -N {self.name}'
        output = os.popen(copy_cmd)

        if len(output.read()) == 0:
            # FIXME very weak way of determining if copied successfully,
            #       but haven't encountered failing to see what that looks like yet
            return True
        return False
