import logging
import requests
from logging import Handler, LogRecord
from agent import Agent

DEFAULT_DEBUG_ENDPOINT = 'http://localhost:8000/send-message/'

DEFAULT_LOG_FORMAT = "%(name)s - %(levelname)s - %(message)s"
DUMMY_LOG_RECORD = LogRecord(name="", level=0, pathname="", lineno=0, msg="", args=(), exc_info=None)
LOG_DEFAULT_ATTRS = set(vars(DUMMY_LOG_RECORD).keys())


class HTTPDebuggerHandler(Handler):
    def __init__(self, agent: Agent, url: str = DEFAULT_DEBUG_ENDPOINT):
        super().__init__()
        self.agent = agent
        self.url = url

    def emit(self, record):
        data = {
            'name': self.agent.id,
            'label': self.agent.name,
            'model': self.agent.model,
            'log_level': record.levelname,
            'message': record.getMessage(),
        }
        extra_attrs = {key: value for key, value in record.__dict__.items() if key not in LOG_DEFAULT_ATTRS}
        data.update(extra_attrs)
        try:
            requests.post(self.url, json=data)
        except requests.exceptions.RequestException:
            # Silently ignore request exceptions, allows operation without an active debugger.
            pass
        except Exception:
            self.handleError(record)


class AgentLogger:
    def __new__(cls, name, agent: Agent):
        logger = logging.getLogger(name)
        # Prevent duplicate loggers.
        if logger.hasHandlers():
            return logger
        logger.setLevel(logging.DEBUG)
        log_console_handler = logging.StreamHandler()
        log_console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        log_console_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_console_handler)
        http_debugger_handler = HTTPDebuggerHandler(agent)
        http_debugger_handler.setLevel(logging.DEBUG)
        logger.addHandler(http_debugger_handler)
        return logger


class Logger:
    def __new__(cls, name):
        logger = logging.getLogger(name)
        # Prevent duplicate loggers.
        if logger.hasHandlers():
            return logger
        logger.setLevel(logging.DEBUG)
        log_console_handler = logging.StreamHandler()
        log_console_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
        log_console_handler.setLevel(logging.DEBUG)
        logger.addHandler(log_console_handler)
        return logger
