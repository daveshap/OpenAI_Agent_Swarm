import dotenv
dotenv.load_dotenv()
from .agent_registry import registry
from .agent.agent import Agent

assistants = [
    {
        'id': 'asst_iZQnpwFSFMlrPOq2lRAVNYKM',
        'name': 'Marketing Expert',
        'description': 'Knows everything about marketing.',
        'begin': False
    },
    {
        'id': 'asst_wjcLG18XQmdlwQbfhdk5uyky',
        'name': 'Network Engineer',
        'description': 'Knows everything about networks',
        'begin': False
    },
    {
        'id': 'asst_YcmuoR4zsnw3yQWisC3ol0SD',
        'name': 'Domain Expert',
        'description': 'Owns design studio. Knows everything design studio needs. Potential client of the Founder\'s startup',
        'begin': False
    },
    {
        'id': 'asst_mzTkBtFbPKdoVfoQmTrOVp2j',
        'name': 'Founder',
        'description': 'Founder of the new AI company that is taking over the world',
        'begin': True
    },
]

for assistant in assistants:
    agent = Agent(assistant['id'], assistant['name'], assistant['description'])
    registry.add_agent(agent)
    agent.init(assistant['begin'])