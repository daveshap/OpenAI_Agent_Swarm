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
parser = argparse.ArgumentParser(description='Load agents configuration from a YAML file.')
parser.add_argument('agentsYAML', nargs='?', help='Path to the agents YAML file.')

# Parse arguments
args = parser.parse_args()

# Check if the agents.yaml file path is provided
if args.agentsYAML is None:
    parser.print_help()
    sys.exit(1)

# Construct the absolute path to the agents.yaml file
yaml_file_path = os.path.join(pathlib.Path(__file__).parent.resolve(), args.agentsYAML)

# Check if the provided file path exists
if not os.path.isfile(yaml_file_path):
    print(f"Error: The file {yaml_file_path} does not exist.")
    sys.exit(1)

with open(yaml_file_path, 'r') as stream:
    agent_properties = yaml.safe_load(stream)
    agents = [Agent(properties) for properties in agent_properties]

print(f"Agents: {agents}")

ctx = Context(client, agents)

network.build(ctx)
threading.Thread(target=agentProcessor.processPendingActions, args=(ctx,)).start()
for agent in agents:
    threading.Thread(target=agentProcessor.processThread, args=(ctx, agent,)).start()

ctx.queues['Boss'].put("Explain how clouds are formed in 100 words or less")