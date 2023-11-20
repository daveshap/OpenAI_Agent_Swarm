from context import Context
from agent import Agent
from execution import Execution

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
    print(f"[{agent.name}]>[ASSIGN TASK {execution.actionId}]>[{execution.arguments['assignee']}] {execution.arguments['task']}")    
    ctx.pendingActions.append({
        "id": execution.actionId,
        "agent": agent.name, 
        "threadId": execution.threadId, 
        "runId": execution.runId, 
        "outputs": {}})

    ctx.agentsWaitingForActions.append(agent.name)

    ctx.queues[execution.arguments['assignee']].put(f"Task id: {execution.actionId}\n{execution.arguments['task']}")