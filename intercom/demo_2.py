import dotenv
dotenv.load_dotenv()
from .agent_registry import registry
from .agent.agent import Agent

assistants = [
    {
        'id': 'asst_uZgjXx1rUvrJOmt1Lf3Dgliq',
        'name': 'Marketing Expert',
        'description': 'Knows everything about marketing.',
        'begin': False
    },
    {
        'id': 'asst_zpn3XAb6pVY30D1zvEvkeRWC',
        'name': 'Network Engineer',
        'description': 'Knows everything about networks',
        'begin': False
    },
    {
        'id': 'asst_7GTjrZGo0il4piEngYWUdSzG',
        'name': 'Domain Expert',
        'description': 'Owns design studio. Knows everything design studio needs. Potential client of the Founder\'s startup',
        'begin': False
    },
    {
        'id': 'asst_4Rgz8esZATBxmDaAqqMJdZ98',
        'name': 'Founder',
        'description': 'Founder of the new AI company that is taking over the world',
        'begin': True
    },
]

for assistant in assistants:
    agent = Agent(assistant['id'], assistant['name'], assistant['description'])
    registry.add_agent(agent)
    agent.init(assistant['begin'])