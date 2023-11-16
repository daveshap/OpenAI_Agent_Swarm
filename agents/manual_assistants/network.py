import queue as queueModule
from context import Context
from agent import Agent

def __buildChannel(ctx: Context, agent: Agent):
    if hasattr(agent, 'channels'):
        for channel in agent.channels:
            newChannel = True
            for existingChannel in ctx.channels:
                if existingChannel['name'] == channel:
                    existingChannel['agents'].append(agent.name)
                    newChannel = False
            if newChannel:
                ctx.channels.append({"name": channel, "agents": [agent.name]})

def build(ctx: Context):
    for agent in ctx.agents:
        # Build private queues
        ctx.queues[agent.name] = queueModule.Queue()
        
        # Build channels
        __buildChannel(ctx, agent)
    print(f"Channels: {ctx.channels}")