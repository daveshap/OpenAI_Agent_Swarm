import time
import json
import agentTools
from context import Context
from agent import Agent
import os
from execution import Execution

class AgentProcessor:
    execution: Execution

    def __init__(self):
            self.execution = Execution()

    def processThread(self, ctx: Context, agent: Agent):
        messages = []

        print(f"[{agent.name}] Id: {agent.id}")
        if hasattr(agent, 'talksTo'):
            print(f"[{agent.name}] Talks to: {agent.talksTo}")
        
        self.execution.threadId = ctx.client.beta.threads.create().id
        print(f"[{agent.name}] Thread {self.execution.threadId}")
        print(f"https://platform.openai.com/playground?mode=assistant&assistant={agent.id}&thread={self.execution.threadId}")
        print("")
        queue = ctx.queues[agent.name]
        waitingForMessages = True
        while True:

            if self.execution.toolStatus.waiting:
                if self.execution.toolStatus.output:
                    ctx.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=self.execution.threadId,
                            run_id=self.execution.runId,
                            tool_outputs=self.execution.toolStatus.output
                        )
                    self.execution.toolStatus.waiting=False
            elif waitingForMessages:
                message = queue.get(block=True)
                if message is not None:
                    ctx.lock.acquire()
                    print(f"[{agent.name}] ACQUIRES LOCK")
                    waitingForMessages = False
                    # print(f"[{agent['name']}] Recieved: {message}")
                    messages.append(message)
                    ctx.client.beta.threads.messages.create(
                        thread_id=self.execution.threadId,
                        content=message,
                        role='user'
                    )

                    run = ctx.client.beta.threads.runs.create(
                        thread_id=self.execution.threadId,
                        assistant_id=agent.id
                    )
                    self.execution.runId=run.id
            else:
                run = ctx.client.beta.threads.runs.retrieve(thread_id=self.execution.threadId, run_id=self.execution.runId)
                if run.status == 'completed':
                    waitingForMessages = True
                    
                    message_list = ctx.client.beta.threads.messages.list(
                        thread_id=self.execution.threadId
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
                        self.execution.actionId=action.id
                        self.execution.arguments=json.loads(action.function.arguments)
                        function_name = action.function.name
                        if function_name == 'sendMessage':
                            output = agentTools.sendMessage(ctx, agent, self.execution)
                        elif function_name == 'broadcast':
                            output = agentTools.broadcast(ctx, agent, self.execution)
                        elif function_name == 'assignTask':
                            output = agentTools.assignTask(ctx, agent, self.execution)
                            submitOutput=False
                        elif function_name == 'resolveTask':
                            output = agentTools.resolveTask(ctx, agent, self.execution)
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
                                thread_id=self.execution.threadId,
                                run_id=self.execution.runId,
                                tool_outputs=outputs
                            )
                        if self.execution.exit:
                            os._exit(0)
                        if ctx.lock.locked():
                            ctx.lock.release()
                        print(f"[{agent.name}] RELEASES LOCK")       
            time.sleep(1)