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
                    # if 'talksTo' in agent:
                    #     for downstreamAgent in agent['talksTo']:
                    #         print(f"[{agent['name']}] Sending message to {downstreamAgent}")
                    #         queues[downstreamAgent].put(retrievedMessage)
                    i+=1
            elif run.status == 'requires_action':
                outputs = []
                for action in run.required_action.submit_tool_outputs.tool_calls:
                    function_name = action.function.name
                    arguments = json.loads(action.function.arguments)
                    if function_name == 'sendMessage':
                        if ('talksTo' in agent) and (arguments['recipient'] in agent['talksTo']):
                            print(f"[{agent['name']}]->[{arguments['recipient']}] {arguments['message']}")
                            queues[arguments['recipient']].put(arguments['message'])
                            outputs.append({
                                "tool_call_id": action.id,
                                "output": "Message sent"
                            })
                        else:
                            print(f"[{agent['name']}] ERROR unkown recipient {arguments['recipient']}")
                    else:
                        print(f"[{agent['name']}] ERROR unkown function {function_name}")
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=outputs
                )
        time.sleep(1)

queues = {}

for agent in agents:
    queues[agent['name']] = queueModule.Queue()
    threading.Thread(target=handleThreadForAgent, args=(agent,)).start()

queues['Uppercase'].put("aaaaa")