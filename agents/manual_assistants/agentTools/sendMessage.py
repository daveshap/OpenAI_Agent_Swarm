import os
from context import Context
from agent import Agent
from execution import Execution

definition=\
    {
        "name": "sendMessage",
        "description": "Send a message to another agent",
        "parameters": {
            "type": "object",
            "properties": {
            "recipient": {
                "type": "string",
                "description": "Agent name to send the message to"
            },
            "message": {
                "type": "string",
                "description": "Message to send"
            }
            },
            "required": [
            "recipient",
            "message"
            ]
        }
    }

def execute(ctx: Context, agent: Agent, execution: Execution):
    if hasattr(agent, 'talksTo') and (execution.arguments['recipient'] in agent.talksTo):
        if execution.arguments['recipient'] == "USER":
            print(f"[{ctx.agent.name}] Result: {execution.arguments['message']}")
            os._exit(0)
        else:
            print(f"[{ctx.agent.name}]->[{execution.arguments['recipient']}] {execution.arguments['message']}")
            
            ctx.queues[execution.arguments['recipient']].put(execution.arguments['message'])
            return {
                "tool_call_id": ctx.action.id,
                "output": "Message sent"
                }
    else:
        print(f"[{agent.name}] ERROR unkown recipient {execution.arguments['recipient']}")