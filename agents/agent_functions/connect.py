import yaml
from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()
import queue as queueModule
import time
import threading
import json

agents_path = 'agents'
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError('The OPENAI_API_KEY environment variable is not set.')

client = OpenAI(api_key=api_key)

# Get the directory name of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the agents.yaml file
yaml_file_path = os.path.join(script_dir, 'agents.yaml')

with open(yaml_file_path, 'r') as stream:
    agents = yaml.safe_load(stream)

queues = {}
channels = []

lock = threading.Lock()

def processSendMessage(agent, outputs, action, arguments):
    if ('talksTo' in agent) and (arguments['recipient'] in agent['talksTo']):
        if arguments['recipient'] == "USER":
            print(f"[{agent['name']}] Result: {arguments['message']}")
            os._exit(0)
        else:
            print(f"[{agent['name']}]->[{arguments['recipient']}] {arguments['message']}")
            
            queues[arguments['recipient']].put(arguments['message'])
            outputs.append({
                "tool_call_id": action.id,
                "output": "Message sent"
                })
    else:
        print(f"[{agent['name']}] ERROR unkown recipient {arguments['recipient']}")

def broadcast(agent, outputs, action, arguments):
    if ('channels' in agent) and (arguments['channel'] in agent['channels']):
        for channel in channels:
            if channel['name'] == arguments['channel']:
                print(f"[{agent['name']}]->({arguments['channel']}) {arguments['message']}")
                for recipient in channel['agents']:
                    if recipient != agent['name']: # Do not queue the message on the agent that sent in
                        queues[recipient].put(arguments['message'])                
        outputs.append({
            "tool_call_id": action.id,
            "output": "Message sent"
            })
    else:
        print(f"[{agent['name']}] ERROR unkown channel {arguments['channel']}")
        outputs.append({
            "tool_call_id": action.id,
            "output": "Unkown channel"
            })

def assignTask(agent, arguments, actionId, threadId, runId):
    print(f"[{agent['name']}]>[ASSIGN TASK {actionId}]>[{arguments['assignee']}] {arguments['task']}")    
    pendingActions.append({
        "id": actionId,
        "agent": agent['name'], 
        "threadId": threadId, 
        "runId": runId, 
        "outputs": {}})

    agentsWaitingForActions.append(agent['name'])

    queues[arguments['assignee']].put(f"Task id: {actionId}\n{arguments['task']}")

def resolveTask(agent, workerOutputs, action, arguments):
    print(f"{arguments}")
    print(f"[{agent['name']}]>[RESOLVE TASK {arguments['id']}] {arguments['result']}")    
    os._exit(0)
    # outputs = []
    # outputs.append({
    #         "tool_call_id": arguments['id'],
    #         "output": arguments['result']
    #         })
    # for pendingAction in pendingActions:
    #     if pendingAction['id'] == arguments['id']:
    #         client.beta.threads.runs.submit_tool_outputs(
    #                     thread_id=pendingAction['threadId'],
    #                     run_id=pendingAction['runId'],
    #                     tool_outputs=outputs
    #                 )
    
    # workerOutputs.append({
    #     "tool_call_id": action.id,
    #     "output": "Task resolved"
    #     })
    
    
def handleThreadForAgent(agent):
    messages = []
    
    print(f"[{agent['name']}] Id: {agent['id']}")
    if 'talksTo' in agent:
        print(f"[{agent['name']}] Talks to: {agent['talksTo']}")
    
    thread = client.beta.threads.create()    
    print(f"[{agent['name']}] Thread {thread.id}")
    
    print("")
    queue = queues[agent['name']]
    waitingForMessages = True
    while True:
        if agent['name'] not in agentsWaitingForActions:
            if waitingForMessages:
                message = queue.get(block=True)
                if message is not None:
                    lock.acquire()
                    print(f"[{agent['name']}] ACQUIRES LOCK")
                    waitingForMessages = False
                    # print(f"[{agent['name']}] Recieved: {message}")
                    messages.append(message)
                    client.beta.threads.messages.create(
                        thread_id=thread.id,
                        content=message,
                        role='user'
                    )

                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=agent['id']
                    )

            else:
                run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
                if run.status == 'completed':
                    waitingForMessages = True
                    
                    message_list = client.beta.threads.messages.list(
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
                        print(f"[{agent['name']}] Message: {retrievedMessage}")
                        i+=1
                    if lock.locked():
                        lock.release()
                    print(f"[{agent['name']}] RELEASES LOCK")
                elif run.status == 'requires_action':
                    outputs = []
                    submitOutput=True
                    for action in run.required_action.submit_tool_outputs.tool_calls:
                        function_name = action.function.name
                        arguments = json.loads(action.function.arguments)
                        if function_name == 'sendMessage':
                            processSendMessage(agent, outputs, action, arguments)
                        elif function_name == 'broadcast':
                            broadcast(agent, outputs, action, arguments)
                        elif function_name == 'assignTask':
                            assignTask(agent, arguments, action.id, thread.id, run.id)                        
                            submitOutput=False
                        elif function_name == 'resolveTask':
                            resolveTask(agent, outputs, action, arguments)
                        else:
                            print(f"[{agent['name']}] ERROR unkown function {function_name}")
                            outputs.append({
                                "tool_call_id": action.id,
                                "output": "Unkown function"
                                })
                        
                        if submitOutput:
                            client.beta.threads.runs.submit_tool_outputs(
                                thread_id=thread.id,
                                run_id=run.id,
                                tool_outputs=outputs
                            )
                        if lock.locked():
                            lock.release()
                        print(f"[{agent['name']}] RELEASES LOCK")
                        
        time.sleep(1)

def buildChannel(agent):
    if 'channels' in agent:
        for channel in agent['channels']:
            newChannel = True
            for existingChannel in channels:
                if existingChannel['name'] == channel:
                    existingChannel['agents'].append(agent['name'])
                    newChannel = False
            if newChannel:
                channels.append({"name": channel, "agents": [agent['name']]})

for agent in agents:
    # Build private queues
    queues[agent['name']] = queueModule.Queue()
    
    # Build channels
    buildChannel(agent)

print(f"Channels: {channels}")

# agent, threadId, runId, outputs
pendingActions = []
agentsWaitingForActions = []
def processPendingActions():
    while True:
        for action in pendingActions:
            if action['outputs']: # Output already set
                client.beta.threads.runs.submit_tool_outputs(
                            thread_id=action['threadId'],
                            run_id=action['runId'],
                            tool_outputs=action['outputs']
                        )
                agentsWaitingForActions.remove(action['agent'])
        time.sleep(1)

threading.Thread(target=processPendingActions, args=()).start()

for agent in agents:
    threading.Thread(target=handleThreadForAgent, args=(agent,)).start()

queues['Boss'].put("Explain how clouds are formed in 100 words or less")