import dotenv
dotenv.load_dotenv()
from agent_registry import registry
from agent.agent import Agent

assistants = [
    {
        'id': 'asst_b5TgVQDd0J0ZsjhjcTnmUEpO',
        'name': 'Marketing Expert',
        'description': 'Knows everything about marketing.',
        'begin': False
    },
    {
        'id': 'asst_x9cF6B4y2U4ByPecOHPqw49C',
        'name': 'Network Engineer',
        'description': 'Knows everything about networks',
        'begin': False
    },
    {
        'id': 'asst_yWRNnIMd3jZ2MIvSQWZC95fx',
        'name': 'Founder',
        'description': 'Founder of the new AI company that is taking over the world',
        'begin': True
    },
]

for assistant in assistants:
    agent = Agent(assistant['id'], assistant['name'], assistant['description'])
    registry.add_agent(agent)
    agent.init(assistant['begin'])