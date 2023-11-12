import json
import os

class AssistantConfig:
    def __init__(self, tools_to_use=None):
        self.tools_to_use = tools_to_use or []
        self.instructions_for_assistant = 'Use the tools to accomplish the task'
        self.files_for_assistant = []  # Local file paths
        self.assistant_details = self._build_assistant_details()

    def _build_assistant_details(self):
        assistant_details = {
            'build_params': {
                'model': "gpt-4-1106-preview",
                'name': "Tool User",
                'description': "Assistant to use tools made by the tool creator.",
                'instructions': self.instructions_for_assistant,
                'tools': [],  # Tools will be added in the loop below
                'file_ids': [],
                'metadata': {},
            },
            'file_paths': self.files_for_assistant,
            'functions': {},  # Functions will be added in the loop below
        }

        # Load tools and their details
        os.makedirs('tools', exist_ok=True)
        if not self.tools_to_use:
            self.tools_to_use = [tool.split('.')[0] for tool in os.listdir('tools') if tool.endswith('.py')]
        for tool in self.tools_to_use:
            with open(f'tools/{tool}.json') as f:
                tool_details = json.load(f)

            with open(f'tools/{tool}.py') as f:
                tool_code = f.read()

            assistant_details['build_params']['tools'].append({
                "type": "function",
                "function": {
                    "name": tool_details['name'],
                    "description": tool_details['description'],
                    "parameters": eval(tool_details['parameters']),
                },
            })
            assistant_details['functions'][tool_details['name']] = tool_code

        return assistant_details
