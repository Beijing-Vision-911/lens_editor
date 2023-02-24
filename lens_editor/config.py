import logging
from configparser import ConfigParser, NoOptionError, NoSectionError
from pathlib import Path

logger = logging.getLogger(__name__)


class Singleton(type):
    _instance = None

    def __call__(cls, *args, **kwargs)-> None:
        if not cls._instance:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Config(metaclass=Singleton):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.parser: ConfigParser = ConfigParser()
        self.load()

    def load(self) -> None:
        if self.path.exists():
            self.parser.read(self.path)
            logger.debug(f"Loading config file from {self.path}")

    def save(self) -> None:
        with open(self.path, "w") as file:
            logger.debug(f"Writing default config file to{self.path}")
            self.parser.write(file)
        logger.debug("config saved")

    def set(self, section: str, option: str, value: str) -> None:
        try:
            self.parser.set(section, option, value)
        except NoSectionError as e:
            logger.debug(e)
            self.parser.add_section(section)
            self.parser.set(section, option, value)
        finally:
            self.save()

    def get(self, section: str, option: str, **kwargs) -> str:
        return self.parser.get(section, option, **kwargs)

    def setup(self, section: str, option: str, default: str) -> str:
        try:
            return self.parser.get(section, option)
        except NoSectionError as e:
            logger.debug(e)
            self.set(section, option, default)
            return default
        except NoOptionError as e:
            logger.debug(e)
            self.set(section, option, default)
            return default


def root_config(path: str) -> None:
    cfg_path: Path = Path(path).expanduser()
    Config._instance = None
    Config._instance = Config.__call__(cfg_path)
