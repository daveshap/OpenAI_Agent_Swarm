class AssistantConfig:
    def __init__(self):
        self.create_tool_function = """
def create_tool(tool_name=None, tool_description=None, tool_parameters=None, tool_code=None, required_action_by_user=None):
    \"\"\"
    returns a tool that can be used by other assistants
    \"\"\"

    # create the tool file
    os.makedirs('tools', exist_ok=True)
    with open(f'tools/{tool_name}.py', 'w') as f:
        f.write(tool_code)

    # create the tool details file
    tool_details = {
        'name': tool_name,
        'description': tool_description,
        'parameters': tool_parameters,
    }

    with open(f'tools/{tool_name}.json', 'w') as f:
        json.dump(tool_details, f, indent=4)

    return_value = f'created tool at tools/{tool_name}.py with details tools/{tool_name}.json\\n\\n'
    return_value += f'There is a required action by the user before the tool can be used: {required_action_by_user}'

    return return_value
        """
        self.files_for_assistant = []
        self.instructions_for_assistant = "You create tools to accomplish arbitrary tasks. Write and run code to implement the interface for these tools using the OpenAI API format. You do not have access to the tools you create. Instruct the user that to use the tool, they will have to create an assistant equipped with that tool, or consult with the AssistantCreationAssistant about the use of that tool in a new assistant."
        self.example_tool = """
def new_tool_name(param1=None, param2='default_value'):
    if not param1: 
        return None
        
    # does something with the parameters to get the result
    intermediate_output = ...
        
    # get the tool output
    tool_output = ...
        
    return tool_output
        """
        self.assistant_details = self._build_assistant_details()

    def _build_assistant_details(self):
        return {
            'build_params' : {
                'model': "gpt-4-1106-preview", 
                'name': "Tool Creator",
                'description': "Assistant to create tools for use in the OpenAI platform by other Assistants.",
                'instructions': self.instructions_for_assistant, 
                'tools': [
                    {
                        "type": "function", 
                        "function": {
                            "name": "create_tool",
                            "description": "returns a tool that can be used by other assistants. specify the tool_name, tool_description, tool_parameters, and tool_code. all of those are required. use the JSON schema for all tool_parameters.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "tool_name": {
                                        "type": "string",
                                        "description": "The name of the tool, using snake_case e.g. new_tool_name",
                                    },
                                    "tool_description": {
                                        "type": "string",
                                        "description": "The description of the tool, e.g. This tool does a computation using param1 and param2 to return a result that ...",
                                    },
                                    "tool_parameters": {
                                        "type": "string",
                                        "description": 'The parameters of the tool, using JSON schema to specify the type and properties for each parameter.\n\ne.g.\n\n{"type": "object", "properties": {"location": {"type": "string", "description": "The city and state e.g. San Francisco, CA"}, "unit": {"type": "string", "enum": ["c", "f"]}}, "required": ["location"]}',
                                    },
                                    "tool_code": {
                                        "type": "string",
                                        "description": f"The code for the tool, e.g. \n{self.example_tool}",
                                    },
                                    "required_action_by_user": {
                                        "type": "string",
                                        "description": "Optional. The action required by the user before the tool can be used, e.g. 'set up API keys for service X and add them as environment variables'. It's important to be as detailed as possible so that these tools can be used for arbitrary tasks. If there is nothing required, do not include this parameter.",
                                    },
                                },
                                "required": ["tool_name", "tool_description", "tool_parameters", "tool_code"],
                            },
                        },
                    },
                ],
                'file_ids': [],
                'metadata': {},
            },
            'file_paths': self.files_for_assistant,
            'functions': {
                'create_tool': self.create_tool_function,
            },
        }
