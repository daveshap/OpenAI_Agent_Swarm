from agents.tool_maker.tool_manager import ToolManager
from pathlib import Path
import os
import json
from agents.agent_builder.create import create_assistants

class AssistantManager:

    def __init__(self, client):
        create_assistants()
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
            raise ValueError(f'{self.assistant_package["name"]} needs to be created using create.py in /agents/agent_builder/')
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
            raise ValueError(f'{name} needs to be created using create.py in /agents/agent_builder/')
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

if __name__ == "__main__":
    from  shared.openai_config import get_openai_client

    client = get_openai_client()

    assistant_manager = AssistantManager(client=client)
    assistant = assistant_manager.get_assistant()
    print(assistant)
