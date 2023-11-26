import time
import json
import agentTools
from context import Context
from agent import Agent
import os
from execution import Execution
from logger import AgentLogger


class AgentProcessor:
    execution: Execution

    def __init__(self, function_manager):
        self.execution = Execution()
        self.function_manager = function_manager

    def processThread(self, ctx: Context, agent: Agent):
        self.log = AgentLogger(agent.name, agent)
        messages = []

        self.log.info(f"Id: {agent.id}")
        if hasattr(agent, 'talksTo'):
            self.log.info(f"Talks to: {agent.talksTo}")
        
        self.execution.threadId = ctx.client.beta.threads.create().id
        self.log.info(f"Thread {self.execution.threadId}")
        self.log.info(f"https://platform.openai.com/playground?mode=assistant&assistant={agent.id}&thread={self.execution.threadId}")
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
                    self.log.info("ACQUIRES LOCK")
                    waitingForMessages = False
                    # self.log.info(f"Recieved: {message}")
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
                        self.log.info(f"Message: {retrievedMessage}")
                        i+=1
                    if ctx.lock.locked():
                        ctx.lock.release()
                    self.log.info("RELEASES LOCK")
                elif run.status == 'requires_action':                    
                    outputs = []
                    submitOutput = True
                    for action in run.required_action.submit_tool_outputs.tool_calls:
                        self.execution.actionId = action.id
                        self.execution.arguments = json.loads(action.function.arguments)
                        function_name = action.function.name
                        self.log.debug(f"Received tool request, ID: {action.id}, tool: {function_name}, arguments: {self.execution.arguments}", extra={'action_id': action.id, 'tool': function_name, 'arguments': self.execution.arguments})
                        output = None
                        if self.function_manager.function_exists(function_name):
                            if function_name == 'assign_task':
                                submitOutput = False
                            success, tool_output, user_message = self.function_manager.run_function(function_name, self.execution.arguments, ctx, agent, self.execution)
                            if success:
                                self.log.debug(f"Tool run {action.id} executed successfully, tool: {function_name}, output: {tool_output}", extra={'action_id': action.id, 'tool': function_name})
                                output = {
                                    "tool_call_id": action.id,
                                    "output": tool_output
                                }
                            else:
                                error_message = f"Tool run {action.id}, error running function {function_name}: {user_message}"
                                self.log.error(error_message, extra={'action_id': action.id, 'tool': function_name})
                                output = {
                                    "tool_call_id": action.id,
                                    "output": error_message,
                                }
                        else:
                            self.log.error(f"Tool run {action.id}, unknown tool {function_name}", extra={'action_id': action.id, 'tool': function_name})
                            output = {
                                "tool_call_id": action.id,
                                "output": "Unkown function"
                            }
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
                        self.log.info("RELEASES LOCK")       
            time.sleep(1)
