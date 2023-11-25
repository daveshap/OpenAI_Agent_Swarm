from abc import abstractmethod

import yaml

from pathlib import Path

from logger import Logger
from doc_parser import func_to_openai_function_spec


class Function:
    def __init__(self):
        self.log = Logger(self.__class__.__name__)

    def set_name(self, name):
        self.name = name

    def set_filepath(self, filepath):
        self.filepath = filepath

    def set_agent(self, agent):
        self.agent = agent

    def set_context(self, context):
        self.context = context

    def set_execution(self, execution):
        self.execution = execution

    def get_config(self):
        filepath = Path(self.filepath)
        config_filepath = filepath.with_suffix(".config.yaml")
        if config_filepath.is_file():
            try:
                self.log.debug(
                    f"Loading configuration for {self.name} from filepath: {config_filepath}"
                )
                with open(config_filepath, "r") as config_file:
                    config = yaml.safe_load(config_file)
                self.log.debug(f"Loaded YAML configuration for {self.name}: {config}")
                return config
            except Exception as e:
                self.log.error(f"Error loading configuration for {self.name}: {str(e)}")
                raise ValueError(f"Failed to load configuration file for {self.name}") from e
        return func_to_openai_function_spec(self.name, self.__call__)

    @abstractmethod
    def __call__(self, **kwargs):
        pass
