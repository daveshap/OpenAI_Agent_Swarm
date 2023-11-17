import os
from context import Context
from agent import Agent

def resolveTask(ctx: Context, agent: Agent, arguments: {}):
    print(f"[{agent.name}]>[RESOLVE TASK {arguments['id']}] {arguments['result']}")
    os._exit(0)
    # outputs = []
    # outputs.append({
    #         "tool_call_id": arguments['id'],
    #         "output": arguments['result']
    #         })
    # for pendingAction in ctx.pendingActions:
    #     if pendingAction['id'] == arguments['id']:
    #         ctx.client.beta.threads.runs.submit_tool_outputs(
    #                     thread_id=pendingAction['threadId'],
    #                     run_id=pendingAction['runId'],
    #                     tool_outputs=outputs
    #                 )
    
    # return {
    #     "tool_call_id": ctx.action.id,
    #     "output": "Task resolved"
    #     }