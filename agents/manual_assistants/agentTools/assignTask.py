from context import Context
from agent import Agent
from execution import Execution
from logger import AgentLogger

definition=\
    {
        "name": "assignTask",
        "description": "Assign a task to the worker agents",
        "parameters": {
            "type": "object",
            "properties": {
            "assignee": {
                "type": "string",
                "description": "Name of the agent assigned to this task"
            },
            "task": {
                "type": "string",
                "description": "Description of the task"
            }
            },
            "required": [
            "description"
            ]
        }
    }

def execute(ctx: Context, agent: Agent, execution: Execution):
    log = AgentLogger(agent.name, agent)
    log.info(f"[ASSIGN TASK {execution.actionId}]>[{execution.arguments['assignee']}] {execution.arguments['task']}", extra={'action_id': execution.actionId, 'task': execution.arguments['task'], 'assignee': execution.arguments['assignee']})
    execution.toolStatus.waiting=True
    ctx.queues[execution.arguments['assignee']].put(f"Task id: {execution.actionId}\n{execution.arguments['task']}")
