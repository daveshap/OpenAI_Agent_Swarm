import os
from context import Context
from agent import Agent

def sendMessage(ctx: Context, agent: Agent, arguments: {}):
    if hasattr(agent, 'talksTo') and (arguments['recipient'] in agent.talksTo):
        if arguments['recipient'] == "USER":
            print(f"[{ctx.agent.name}] Result: {arguments['message']}")
            os._exit(0)
        else:
            print(f"[{ctx.agent.name}]->[{arguments['recipient']}] {arguments['message']}")
            
            ctx.queues[arguments['recipient']].put(arguments['message'])
            return {
                "tool_call_id": ctx.action.id,
                "output": "Message sent"
                }
    else:
        print(f"[{agent.name}] ERROR unkown recipient {arguments['recipient']}")