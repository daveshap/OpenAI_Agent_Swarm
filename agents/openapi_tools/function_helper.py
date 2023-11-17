import jsonref
from bs4 import BeautifulSoup
import yaml  # Make sure to install pyyaml
import logging
from copy import deepcopy

class OpenApiFunctionHelper:
    """
    A class for processing an OpenAPI specification and transforming it into a format 
    suitable for use with an OpenAI assistant. It supports both JSON and YAML formats 
    of OpenAPI specifications and can handle references and HTML content within the spec.

    The class parses an OpenAPI spec, cleans it up, and converts it into a collection 
    of function definitions that can be used by an OpenAI assistant.

    Usage:
        with open("path/to/openapi.yaml", "r") as file:
            helper = OpenApiFunctionHelper(file.read())
            functions = helper.assistant_functions
            print(functions)
    """

    def __init__(self, openapi_spec):
        """
        Initializes the OpenApiFunctionHelper with an OpenAPI specification.

        Args:
            openapi_spec (str or dict): The OpenAPI specification as a string 
            in either JSON or YAML format, or as a parsed dictionary.
        """
        if isinstance(openapi_spec, str):
            try:
                openapi_spec = yaml.safe_load(openapi_spec)  # Handles both YAML and JSON
            except yaml.YAMLError as e:
                logging.error(f"Error parsing spec: {e}")
                raise

        self.openapi_spec = deepcopy(openapi_spec)
        self.clean_openapi_schema()
        self.assistant_functions = self.openapi_to_functions()

    def extract_and_clean_description(self, spec):
        """
        Extracts and cleans the description from a single OpenAPI path item or operation object.
        Removes any HTML tags and returns plain text.

        Args:
            spec (dict): A dictionary representing a single path item or operation object 
            in an OpenAPI spec.

        Returns:
            str: The cleaned description text.
        """
        desc = spec.get("description") or spec.get("summary", "")
        if "<" in desc and ">" in desc:  # Check for HTML-like tags
            soup = BeautifulSoup(desc, "html.parser")
            desc = soup.get_text()
        return desc

    def clean_openapi_schema(self):
        """
        Cleans the OpenAPI schema by iterating over all paths and operations, 
        resolving any JSON references and cleaning HTML content from descriptions.
        """
        for path, methods in self.openapi_spec["paths"].items():
            for method, spec_with_ref in methods.items():
                spec = jsonref.replace_refs(spec_with_ref)
                spec["description"] = self.extract_and_clean_description(spec)

    def openapi_to_functions(self):
        """
        Converts the OpenAPI specification into a list of function definitions suitable
        for use with an OpenAI assistant.

        Returns:
            list: A list of dictionaries, each representing a function definition.
        """
        functions = []
        for path, methods in self.openapi_spec["paths"].items():
            for method, spec in methods.items():
                function_name = spec.get("operationId")
                desc = self.extract_and_clean_description(spec)

                schema = OpenApiFunctionHelper.build_schema(spec)

                functions.append(
                    {"name": function_name, "description": desc, "parameters": schema}
                )

        return functions

    @classmethod
    def build_schema(cls, spec):
        """
        Builds a schema from the OpenAPI spec for use with an assistant.

        Args:
            spec (dict): The OpenAPI specification for a single API endpoint.

        Returns:
            dict: The schema in a format suitable for use with an assistant.
        """
        schema = {"type": "object", "properties": {}}

        # Extract schema for request body
        req_body = (
            spec.get("requestBody", {})
            .get("content", {})
            .get("application/json", {})
            .get("schema")
        )
        if req_body:
            schema["properties"]["requestBody"] = req_body

        # Extract schema for parameters
        params = spec.get("parameters", [])
        if params:
            param_properties = {
                param["name"]: param["schema"]
                for param in params
                if "schema" in param
            }
            schema["properties"]["parameters"] = {
                "type": "object",
                "properties": param_properties,
            }

        return schema

if __name__ == "__main__":
    yaml_path = "oas/openapi.yaml"
    json_path = "oas/financesV0.json"
    with open(yaml_path, "r") as file:
        functions = OpenApiFunctionHelper(file.read()).assistant_functions
        print(functions)
    with open(json_path, "r") as file:
        functions = OpenApiFunctionHelper(file.read()).assistant_functions
        print(functions)
