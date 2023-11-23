import os
from context import Context
from agent import Agent
from execution import Execution
from logger import AgentLogger

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
    log = AgentLogger(agent.name, agent)
    if hasattr(agent, 'talksTo') and (execution.arguments['recipient'] in agent.talksTo):
        if execution.arguments['recipient'] == "USER":
            log.info(f"Result: {execution.arguments['message']}", extra={'result': execution.arguments['message']})
            os._exit(0)
        else:
            log.info(f"[{execution.arguments['recipient']}] {execution.arguments['message']}", extra={'recipient': execution.arguments['recipient']})
            ctx.queues[execution.arguments['recipient']].put(execution.arguments['message'])
            return {
                "tool_call_id": ctx.action.id,
                "output": "Message sent"
                }
    else:
        log.error(f"Unkown recipient {execution.arguments['recipient']}")
