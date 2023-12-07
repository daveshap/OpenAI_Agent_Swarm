# OpenApiFunctionHelper

## Introduction

`OpenApiFunctionHelper` is a Python class designed to process OpenAPI specifications and convert them into a format suitable for use with OpenAI assistants. It supports both JSON and YAML formats of OpenAPI specifications and can handle references and HTML content within the spec. The class provides a convenient way to parse an OpenAPI spec, clean it up, and convert it into a collection of function definitions that can be utilized by an OpenAI assistant.

## Installation

Before you begin, ensure that you have Python installed on your system. This class requires Python 3.6 or later.

You will also need to install the following Python packages:

- `beautifulsoup4`
- `pyyaml`
- `jsonref`

You can install these packages using pip:

```bash
pip install -r requirements.txt
```

## Usage

To use `OpenApiFunctionHelper`, follow these steps:

1. Import the class into your Python script.
2. Load your OpenAPI specification (either in JSON or YAML format).
3. Create an instance of `OpenApiFunctionHelper` using the loaded spec.
4. Access the `assistant_functions` property to get the converted functions.

### Example

```python
from openapi_tools import OpenApiFunctionHelper

# Load an OpenAPI specification from a file
with open("path/to/openapi.yaml", "r") as file:
    openapi_spec = file.read()

# Create an instance of OpenApiFunctionHelper
helper = OpenApiFunctionHelper(openapi_spec)

# Get the list of assistant functions
functions = helper.assistant_functions

# Print the extracted functions
print(functions)
```