from context import Context
from agent import Agent

def assignTask(ctx: Context, agent: Agent, actionId: str, arguments: {}, threadId: str, runId: str):
    print(f"[{agent.name}]>[ASSIGN TASK {actionId}]>[{arguments['assignee']}] {arguments['task']}")    
    ctx.pendingActions.append({
        "id": actionId,
        "agent": agent.name, 
        "threadId": threadId, 
        "runId": runId, 
        "outputs": {}})

    ctx.agentsWaitingForActions.append(agent.name)

    ctx.queues[arguments['assignee']].put(f"Task id: {actionId}\n{arguments['task']}")