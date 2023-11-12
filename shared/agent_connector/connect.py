import yaml
from shared.openai_config import get_openai_client 
import os
import queue as queueModule
import time
import threading

agents_path = 'agents'
client = get_openai_client()

# Get the directory name of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the agents.yaml file
yaml_file_path = os.path.join(script_dir, 'agents.yaml')

with open(yaml_file_path, 'r') as stream:
    agents = yaml.safe_load(stream)

messageQueue = []

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
        if waitingForMessages:
            message = queue.get(block=True)
            if message is not None:
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
                    if 'talksTo' in agent:
                        for downstreamAgent in agent['talksTo']:
                            print(f"[{agent['name']}] Sending message to {downstreamAgent}")
                            queues[downstreamAgent].put(retrievedMessage)
                    print("")
                    i+=1     
        time.sleep(1)

queues = {}

for agent in agents:
    queues[agent['name']] = queueModule.Queue()
    threading.Thread(target=handleThreadForAgent, args=(agent,)).start()

queues['Uppercase'].put("aaaaa")