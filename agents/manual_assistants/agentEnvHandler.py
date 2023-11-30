from agent import Agent
import yaml

def saveId(agentsIdsFile: str, agent: Agent):
    with open(agentsIdsFile, 'r') as file:
        data = yaml.safe_load(file) or []

    data.extend([{"name": agent.name, "id": agent.id}])
    with open(agentsIdsFile, 'w') as file:
        yaml.dump(data, file)