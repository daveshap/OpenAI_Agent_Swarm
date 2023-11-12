import json


class ToolManager:
    @staticmethod
    def tool_from_function_schema(schema):
        """takes a JSON schema and wraps in an OpenAI specified tool structure"""
        tool = f"""{{
        "type":"function",
        "function": {json.dumps(schema)}}}
        """
        tool = json.loads(tool)
        return tool

    @staticmethod
    def schema_from_response(response):
        """Takes an agent response and forms a JSON schema"""
        function_request_obj = json.loads(response)
        name = function_request_obj["name"]
        description = function_request_obj["description"]
        schema = function_request_obj["schema"]
        schema = rf"""{{
        "name": "{name}",
        "description": "{description}",
        "parameters": 
            {schema}
        }}"""
        return json.loads(schema)
