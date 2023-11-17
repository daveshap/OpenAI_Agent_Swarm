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
import agentProcessor

dotenv.load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError('The OPENAI_API_KEY environment variable is not set.')

client = OpenAI(api_key=api_key)

# Setup argument parser
parser = argparse.ArgumentParser(description='Load agents configuration its configuration folder.')
parser.add_argument('agentsDefinitionFolder', nargs='?', help='Path to the agents definition folder. Should contain a "agent.yaml" file')

# Parse arguments
args = parser.parse_args()

# Check if the agents.yaml file path is provided
if args.agentsDefinitionFolder is None:
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
agentsEnv = os.path.join(workDir, args.agentsDefinitionFolder, "agents.env")
if os.path.isfile(agentsEnv):
    with open(agentsEnv, 'r') as stream:
        envProperties = yaml.safe_load(stream)
        for properties in envProperties: # For each agent
            for agent in agents: # Find its definition
                if agent.name == properties['name']:
                    if not hasattr(agent, 'id'): # If ID is not hardcoded set it
                        agent.id = properties['id']

print(f"Agents: {agents}")

# Create new assistants
for agent in agents:
    if not hasattr(agent, 'id'): # It's a new agent
        print("create assistant") # TODO

network.build(ctx)
threading.Thread(target=agentProcessor.processPendingActions, args=(ctx,)).start()
for agent in agents:
    threading.Thread(target=agentProcessor.processThread, args=(ctx, agent,)).start()

for agent in agents:
    if hasattr(agent, 'innitMessage'):
        ctx.queues[agent.name].put(agent.innitMessage)