import time
import json
import agentFunctions
from context import Context
from agent import Agent

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
                        if function_name == 'sendMessage':
                            output = agentFunctions.sendMessage(ctx, agent, arguments)
                        elif function_name == 'broadcast':
                            output = agentFunctions.broadcast(ctx, agent, arguments, action.id)
                        elif function_name == 'assignTask':
                            output = agentFunctions.assignTask(ctx, agent, action.id, arguments, thread.id, run.id)                        
                            submitOutput=False
                        elif function_name == 'resolveTask':
                            output = agentFunctions.resolveTask(ctx, agent, arguments)
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
                        if ctx.lock.locked():
                            ctx.lock.release()
                        print(f"[{agent.name}] RELEASES LOCK")
                        
        time.sleep(1)