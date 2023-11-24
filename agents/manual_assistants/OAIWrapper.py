from agent import Agent
from openai import OpenAI
from function_manager import FunctionManager


def createAssistant(client: OpenAI, agent: Agent, function_manager: FunctionManager):
    toolList = []
    if hasattr(agent, "tools"):
        for tool in agent.tools:
            if function_manager.function_exists(tool):
                toolDict = {"type": "function", "function": function_manager.get_function_config(tool)}
                toolList.append(toolDict)
    print(toolList)
    assistant = client.beta.assistants.create(
        name=agent.name,
        instructions=agent.instructions,
        tools=toolList,
        model=agent.model
    )
    agent.id = assistant.id
