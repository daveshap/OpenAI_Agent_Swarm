agents = {}

def add_agent(agent):
    agents[agent.id] = agent

def get_agent(agent_id):
    return agents[agent_id] if agent_id in agents else None

def get_agents():
    return list(agents.values())