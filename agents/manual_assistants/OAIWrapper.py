import sys

from agent import Agent
from openai import OpenAI, NotFoundError
from logger import AgentLogger
from function_manager import FunctionManager
from template_manager import TemplateManager


class OAIWrapper:

    def __init__(self, client: OpenAI, agent: Agent, function_manager: FunctionManager, template_manager: TemplateManager):
        self.client = client
        self.agent = agent
        self.function_manager = function_manager
        self.template_manager = template_manager
        self.log = AgentLogger(self.agent.name, self.agent)

    def createAssistant(self):
        assistant = self.client.beta.assistants.create(
            name=self.agent.name,
            instructions='<placeholder>',
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
                instructions=self.getAgentInstructions(),
                tools=toolList,
                model=self.agent.model
            )
            self.log.debug(f"Updated existing assistant: {self.agent.name}")
        except NotFoundError as e:
            self.log.error(f"Assistant {self.agent.name} not found: {e}")
            self.log.error("Remove the cached assistants .env file in the definition directory and try again.")
            sys.exit(1)

    def getAgentInstructions(self):
        success, instructions, user_message = self.template_manager.render_agent_template(self.agent)
        if success:
            self.log.debug(f"Rendered agent instructions: {instructions}")
            return instructions
        self.log.error(user_message)
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
