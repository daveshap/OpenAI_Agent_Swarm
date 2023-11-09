import yaml

def load_agents_yaml(file_path):
    with open(file_path, 'r') as stream:
        agents = yaml.safe_load(stream)
    return agents

# Assuming agents.yaml is in the same directory as this script
file_path = 'agents.yaml'
agents = load_agents_yaml(file_path)

for agent in agents:
    print(f"Name: {agent['name']}")
    print(f"Id: {agent['id']}")
    if 'talksTo' in agent:
        print(f"Talks to: {agent['talksTo']}")
    print("")