import sys

from agent import Agent
from openai import OpenAI, NotFoundError
from logger import AgentLogger
from function_manager import FunctionManager


class OAIWrapper:

    def __init__(self, client: OpenAI, agent: Agent, function_manager: FunctionManager):
        self.client = client
        self.agent = agent
        self.function_manager = function_manager
        self.log = AgentLogger(self.agent.name, self.agent)

    def createAssistant(self):
        assistant = self.client.beta.assistants.create(
            name=self.agent.name,
            instructions=self.agent.instructions,
            model=self.agent.model
        )
        self.agent.id = assistant.id
        self.log.info(f"Created assistant: {self.agent.name}")

    def updateAssistant(self):
        toolList = self.getAgentTools()
        try:
            self.client.beta.assistants.update(
                assistant_id=self.agent.id,
                name=self.agent.name,
                instructions=self.agent.instructions,
                tools=toolList,
                model=self.agent.model
            )
            self.log.debug(f"Updated existing assistant: {self.agent.name}")
        except NotFoundError as e:
            self.log.error(f"Assistant {self.agent.name} not found: {e}")
            self.log.error("Remove the cached assistants .env file in the definition directory and try again.")
            sys.exit(1)

    def getAgentTools(self):
        toolList = []
        if hasattr(self.agent, "tools"):
            for tool in self.agent.tools:
                if self.function_manager.function_exists(tool):
                    toolDict = {"type": "function", "function": self.function_manager.get_function_config(tool)}
                    toolList.append(toolDict)
        self.log.debug(f"Tool list: {toolList}", extra={"toolList": toolList})
        return toolList
