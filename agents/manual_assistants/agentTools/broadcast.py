from context import Context
from agent import Agent
from execution import Execution

definition=\
    {
        "name": "broadcast",
        "description": "Broadcast a message on a channel",
        "parameters": {
            "type": "object",
            "properties": {
            "channel": {
                "type": "string",
                "description": "Channel name to broadcast the message to"
            },
            "message": {
                "type": "string",
                "description": "Message to broadcast"
            }
            },
            "required": [
            "channel",
            "message"
            ]
        }
    }


def execute(ctx: Context, agent: Agent, execution: Execution):
    if hasattr(agent, 'channels') and (execution.arguments['channel'] in agent.channels):
        for channel in ctx.channels:
            if channel['name'] == execution.arguments['channel']:
                print(f"[{agent.name}]->({execution.arguments['channel']}) {execution.arguments['message']}")
                for recipient in channel['agents']:
                    if recipient != agent.name: # Do not queue the message on the agent that sent in
                        ctx.queues[recipient].put(execution.arguments['message'])                
        return {
            "tool_call_id": execution.actionId,
            "output": "Message sent"
            }
    else:
        print(f"[{agent.name}] ERROR unkown channel {execution.arguments['channel']}")
        return {
            "tool_call_id": execution.actionId,
            "output": "Unkown channel"
            }