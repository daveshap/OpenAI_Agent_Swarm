from agent import Agent
from openai import OpenAI
from agentTools import *

def createAssistant(client: OpenAI, agent: Agent):
    toolList=[]
    if hasattr(agent, "tools"):
        for tool in agent.tools:
            toolClass=globals().get(tool, None)
            toolDict={"type": "function", "function": toolClass.definition}
            toolList.append(toolDict)
    print(toolList)
    assistant = client.beta.assistants.create(
        name=agent.name,
        instructions=agent.instructions,
        tools=toolList,
        model=agent.model
    )
    agent.id=assistant.id