from context import Context
from agent import Agent

def broadcast(ctx: Context, agent: Agent, arguments: {}, actionId: str):
    if hasattr(agent, 'channels') and (arguments['channel'] in agent.channels):
        for channel in ctx.channels:
            if channel['name'] == arguments['channel']:
                print(f"[{agent.name}]->({arguments['channel']}) {arguments['message']}")
                for recipient in channel['agents']:
                    if recipient != agent.name: # Do not queue the message on the agent that sent in
                        ctx.queues[recipient].put(arguments['message'])                
        return {
            "tool_call_id": actionId,
            "output": "Message sent"
            }
    else:
        print(f"[{agent.name}] ERROR unkown channel {arguments['channel']}")
        return {
            "tool_call_id": actionId,
            "output": "Unkown channel"
            }