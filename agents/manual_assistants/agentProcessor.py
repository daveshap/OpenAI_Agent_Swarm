import time
import json
import agentTools
from context import Context
from agent import Agent
import os
from execution import Execution

def processPendingActions(ctx: Context):
    while True:
        for action in ctx.pendingActions:
            if action['outputs']: # Output already set
                ctx.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=action['threadId'],
                            run_id=action['runId'],
                            tool_outputs=action['outputs']
                        )
                ctx.agentsWaitingForActions.remove(action['agent'])
        time.sleep(1)

def processThread(ctx: Context, agent: Agent):
    messages = []
    
    print(f"[{agent.name}] Id: {agent.id}")
    if hasattr(agent, 'talksTo'):
        print(f"[{agent.name}] Talks to: {agent.talksTo}")
    
    thread = ctx.client.beta.threads.create()    
    print(f"[{agent.name}] Thread {thread.id}")
    print(f"https://platform.openai.com/playground?mode=assistant&assistant={agent.id}&thread={thread.id}")
    print("")
    queue = ctx.queues[agent.name]
    waitingForMessages = True
    while True:
        if agent.name not in ctx.agentsWaitingForActions:
            if waitingForMessages:
                message = queue.get(block=True)
                if message is not None:
                    ctx.lock.acquire()
                    print(f"[{agent.name}] ACQUIRES LOCK")
                    waitingForMessages = False
                    # print(f"[{agent['name']}] Recieved: {message}")
                    messages.append(message)
                    ctx.client.beta.threads.messages.create(
                        thread_id=thread.id,
                        content=message,
                        role='user'
                    )

                    run = ctx.client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=agent.id
                    )

            else:
                run = ctx.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run.status == 'completed':
                    waitingForMessages = True
                    
                    message_list = ctx.client.beta.threads.messages.list(
                        thread_id=thread.id
                    )
                    retrievedMessages = []
                    for datum in message_list.data:
                        for content in datum.content:
                            retrievedMessages.append(content.text.value)            
                    retrievedMessages.reverse()
                
                    i = len(messages)
                    while i < len(retrievedMessages):
                        retrievedMessage=retrievedMessages[i]
                        messages.append(retrievedMessage)
                        print(f"[{agent.name}] Message: {retrievedMessage}")
                        i+=1
                    if ctx.lock.locked():
                        ctx.lock.release()
                    print(f"[{agent.name}] RELEASES LOCK")
                elif run.status == 'requires_action':                    
                    outputs = []
                    submitOutput=True
                    for action in run.required_action.submit_tool_outputs.tool_calls:

                        function_name = action.function.name
                        arguments = json.loads(action.function.arguments)
                        execution = Execution(threadId=thread.id, runId=run.id, actionId=action.id, arguments=arguments)
                        if function_name == 'sendMessage':
                            output = agentTools.sendMessage.execute(ctx, agent, execution)
                        elif function_name == 'broadcast':
                            output = agentTools.broadcast.execute(ctx, agent, execution)
                        elif function_name == 'assignTask':
                            output = agentTools.assignTask.execute(ctx, agent, execution)                        
                            submitOutput=False
                        elif function_name == 'resolveTask':
                            output = agentTools.resolveTask.execute(ctx, agent, execution)
                        else:
                            print(f"[{agent.name}] ERROR unkown function {function_name}")
                            output = {
                                "tool_call_id": action.id,
                                "output": "Unkown function"
                                }
                        if output:
                                outputs.append(output)
                        if submitOutput:
                            ctx.client.beta.threads.runs.submit_tool_outputs(
                                thread_id=thread.id,
                                run_id=run.id,
                                tool_outputs=outputs
                            )
                        if execution.exit:
                            os._exit(0)
                        if ctx.lock.locked():
                            ctx.lock.release()
                        print(f"[{agent.name}] RELEASES LOCK")
                        
        time.sleep(1)