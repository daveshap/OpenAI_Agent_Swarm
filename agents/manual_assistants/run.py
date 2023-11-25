import yaml
from openai import OpenAI
import os
import threading
import dotenv
import argparse
import sys
import pathlib

from context import Context
import network
from agent import Agent
from agentProcessor import AgentProcessor
from function_manager import FunctionManager
import OAIWrapper
import agentEnvHandler

dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError('The OPENAI_API_KEY environment variable is not set.')

client = OpenAI(api_key=api_key)

# Setup argument parser
parser = argparse.ArgumentParser(description='Load agents configuration from its configuration folder.')
parser.add_argument('--agents-definition-folder', dest='agentsDefinitionFolder', required=False, help='Path to the agents definition folder. Should contain an "agent.yaml" file')

# Parse arguments
args = parser.parse_args()

# Check if the agents-definition-folder argument was passed
if not args.agentsDefinitionFolder:
    parser.print_help()
    sys.exit(1)

# Construct the absolute path to the agents.yaml file
workDir = pathlib.Path(__file__).parent.resolve()
agentsYAML = os.path.join(workDir, args.agentsDefinitionFolder, "agents.yaml")

# Check if the provided file path exists
if not os.path.isfile(agentsYAML):
    print(f"Error: The file {agentsYAML} does not exist.")
    sys.exit(1)

with open(agentsYAML, 'r') as stream:
    agentsProperties = yaml.safe_load(stream)
    agents = [Agent(properties) for properties in agentsProperties]

ctx = Context(client, agents)

# LOAD ENV IDs
agentsIdsFile = os.path.join(workDir, args.agentsDefinitionFolder, "agentsIds.env")
# Ensure the file exists by opening it in append mode, then immediately close it
with open(agentsIdsFile, 'a'):
    pass

with open(agentsIdsFile, 'r') as stream:
    agentsIds = yaml.safe_load(stream)
    if agentsIds:
        for properties in agentsIds: # For each agent
            for agent in agents: # Find its definition
                if agent.name == properties['name']:
                    if not hasattr(agent, 'id'): # If ID is not hardcoded set it
                        agent.id = properties['id']

print(f"Agents: {agents}")

function_manager = FunctionManager()
function_manager.load_functions()

# Create new assistants
for agent in agents:
    if not hasattr(agent, 'id'): # It's a new agent
        OAIWrapper.createAssistant(client, agent, function_manager)
        agentEnvHandler.saveId(agentsIdsFile, agent)

network.build(ctx)

for agent in agents:
    processor = AgentProcessor(function_manager)
    threading.Thread(target=processor.processThread, args=(ctx, agent,)).start()

for agent in agents:
    if hasattr(agent, 'initMessage'):
        ctx.queues[agent.name].put(agent.initMessage)
