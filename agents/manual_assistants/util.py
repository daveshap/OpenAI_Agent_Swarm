import os
import re
import inspect


def get_file_directory():
    filepath = inspect.stack()[1].filename
    return os.path.dirname(os.path.abspath(filepath))


def snake_to_class(string):
    parts = string.split("_")
    return "".join(word.title() for word in parts)


def get_environment_variable(name, default=None):
    return os.environ.get(f"HAAS_{name.upper()}", default)


def get_environment_variable_list(name):
    var_list = get_environment_variable(name)
    return split_on_delimiter(var_list, ":") if var_list else None


def split_on_delimiter(string, delimiter=","):
    return [x.strip() for x in string.split(delimiter)]


def remove_prefix(text, prefix):
    pattern = r"(?i)^" + re.escape(prefix)
    return re.sub(pattern, "", text)
