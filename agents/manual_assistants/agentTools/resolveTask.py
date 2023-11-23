from context import Context
from agent import Agent
from execution import Execution
from logger import AgentLogger

definition=\
    {
        "name": "resolveTask",
        "description": "Send final task results to the boss agent",
        "parameters": {
            "type": "object",
            "properties": {
            "id": {
                "type": "string",
                "description": "Task id provided when the task was assigned"
            },
            "result": {
                "type": "string",
                "description": "Result of the task"
            }
            },
            "required": [
            "description"
            ]
        }
    }


def execute(ctx: Context, agent: Agent, execution: Execution):
    log = AgentLogger(agent.name, agent)
    log.info(f"[RESOLVE TASK {execution.arguments['id']}] {execution.arguments['result']}", extra={'result': execution.arguments['result']})
    outputs = []
    outputs.append({
            "tool_call_id": execution.arguments['id'],
            "output": execution.arguments['result']
            })
    for pendingAction in ctx.pendingActions:
        if pendingAction['id'] == execution.arguments['id']:
            pendingAction['outout']=outputs
    execution.exit = True
    return {
        "tool_call_id": execution.actionId,
        "output": "Task resolved"
        }
