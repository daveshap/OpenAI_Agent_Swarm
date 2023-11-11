"""
create a tool-creator assistant using the assistant creation API
"""

import json
import os

from shared.utils import chat as chat_loop
from shared.openai_config import get_openai_client 

client = get_openai_client()

def create_tool_creator(assistant_details):
    # create the assistant
    tool_creator = client.beta.assistants.create(**assistant_details["build_params"])

    print(f"Created assistant to create tools: {tool_creator.id}\n\n" + 90*"-" + "\n\n", flush=True)

    # save the assistant info to a json file
    info_to_export = {
        "assistant_id": tool_creator.id,
        "assistant_details": assistant_details,
    }

    os.makedirs('assistants', exist_ok=True)
    with open('assistants/tool_creator.json', 'w') as f:
        json.dump(info_to_export, f, indent=4)

    return tool_creator

def talk_to_tool_creator(assistant_details):
    """
    talk to the assistant to create tools
    """

    # check if json file exists
    try:
        os.makedirs('assistants', exist_ok=True)
        with open('assistants/tool_creator.json') as f:
            create_new = input(f'Assistant details found in tool_creator.json. Create a new assistant? [y/N]')
            if create_new == 'y':
                raise Exception("User wants a new assistant")
            assistant_from_json = json.load(f)
            tool_creator = client.beta.assistants.retrieve(assistant_from_json['assistant_id'])
            print(f"Loaded assistant details from tool_creator.json\n\n" + 90*"-" + "\n\n", flush=True)
            print(f'Assistant {tool_creator.id}:\n')
            assistant_details = assistant_from_json["assistant_details"]
    except:
        tool_creator = create_tool_creator(assistant_details)

    # load the functions into the execution environment
    functions = assistant_details["functions"]
    for func in functions:
        # define the function in this execution environment
        exec(functions[func], globals())
    
        # add the function to the assistant details
        functions.update({func: eval(func)})

    # Create thread
    thread = client.beta.threads.create()

    chat_loop(client, thread, tool_creator, functions)
