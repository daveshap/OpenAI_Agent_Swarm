import threading
import openai

from agent import Agent

class Context:
    def __init__(self, client: openai.Client, agents: [Agent]):
        self.client = client
        self.queues = {}
        self.agents = agents
        self.pendingActions = []
        self.channels = []
        self.lock = threading.Lock()        
        self.outputs = []
        
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)