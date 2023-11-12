import dotenv
dotenv.load_dotenv()
from agent_registry import registry
from agent.agent import Agent

assistants = [
    {
        'id': 'asst_4XixOcWw4Ut9Kz7Pv98dIxo6',
        'name': 'Marketing Expert',
        'description': 'Knows everything about marketing.',
        'begin': False
    },
    {
        'id': 'asst_dH1T9lUUD2aef21aglI9iVcw',
        'name': 'Network Engineer',
        'description': 'Knows everything about networks',
        'begin': False
    },
    {
        'id': 'asst_KEtj0v4T2QHYevcIKTeAtrRn',
        'name': 'Domain Expert',
        'description': 'Owns design studio. Knows everything design studio needs. Potential client of the Founder\'s startup',
        'begin': False
    },
    {
        'id': 'asst_cLIyeNLWz6q1hx1HZDRn9K86',
        'name': 'Founder',
        'description': 'Founder of the new AI company that is taking over the world',
        'begin': True
    },
]

for assistant in assistants:
    agent = Agent(assistant['id'], assistant['name'], assistant['description'])
    registry.add_agent(agent)
    agent.init(assistant['begin'])