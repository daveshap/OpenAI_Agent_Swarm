from tool_manager import ToolManager
from pathlib import Path
import os
import json


class AssistantManager:
    request_function_tool = r"""{
    "name": "function_request",
    "description": "request an authority to grant you access to a new function",
    "parameters": {
        "type": "object",
        "properties": {
        "name": {
            "type": "string",
            "description": "name of the function"
        },
        "description": {
            "type": "string",
            "description": "expected function behaviour"
        },
        "schema": {
            "type": "string",
            "description": "the input arguments for the requested function following the JOSN schema in a format ready to be serialized"
        }
        },
        "required": [
        "name",
        "schema"
        ]
    }
    }"""

    def __init__(self, client):
        self.client = client
        self.assistant = None
        Path(__file__).absolute().parent
        tools_path = os.path.join(
            Path(__file__).absolute().parent, "tool_creator_metadata.json"
        )
        with open(tools_path, "r") as file:
            self.assistant_package = json.load(file)

    def get_assistant(self):
        """Retrieve or create an assistant for testing this functionality"""
        if not self.assistant_package["name"] in [
            assistant.name for assistant in self.client.beta.assistants.list()
        ]:
            assistant = self.make_tool_creation_assistant()
        else:
            assistant_dict = {
                assistant.name: assistant.id
                for assistant in self.client.beta.assistants.list()
            }
            assistant = self.client.beta.assistants.retrieve(
                assistant_id=assistant_dict[self.assistant_package["name"]]
            )
        self.assistant = assistant
        return assistant

    def get_coding_assistant(self):
        """Retrieve or create an assistant for testing this functionality"""
        name = "temporary_function_writer"
        if not name in [
            assistant.name for assistant in self.client.beta.assistants.list()
        ]:
            assistant = self.make_coding_assistant()
        else:
            assistant_dict = {
                assistant.name: assistant.id
                for assistant in self.client.beta.assistants.list()
            }
            assistant = self.client.beta.assistants.retrieve(
                assistant_id=assistant_dict[name]
            )
        self.assistant = assistant
        return assistant

    def make_tool_creation_assistant(self):
        tools = [
            ToolManager.tool_from_function_schema(
                json.loads(AssistantManager.request_function_tool)
            )
        ]
        assistant = self.client.beta.assistants.create(
            model=self.assistant_package["model"],
            description=self.assistant_package["description"],
            instructions=self.assistant_package["instructions"],
            name=self.assistant_package["name"],
            tools=tools,
        )
        return assistant

    def make_coding_assistant(self):
        code_assistant = self.client.beta.assistants.create(
            model="gpt-4-1106-preview",
            instructions="you will be provided a json schema of an OpenAI function tool from an API not a human user. The json will contain all information about the function you will need to write it in python code. You will return only the python function you wrote and no additional text as you are talking to an API and extraneous output will cause execution errors. You must always implement the actual code. Generic placeholders or pseudo code will break the api. If you need clarification to write real functioning code, request for extra info in arguments without creating a real function or valid schema",
            name="temporary_function_writer",
        )
        return code_assistant


if __name__ == "__main__":
    from shared.openai_config import get_openai_client
    client = get_openai_client()
    
    assistant_manager = AssistantManager(client=client)
    assistant = assistant_manager.get_assistant()
    print(assistant)
