from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()

agents_path = 'agents'
api_key = os.getenv('OPENAI_API_KEY')
if api_key is None:
    raise ValueError('The OPENAI_API_KEY environment variable is not set.')

client = OpenAI(api_key=api_key)

# Check if the 'agents' folder is empty or doesn't exist
if not os.path.exists(agents_path) or not os.path.isdir(agents_path) or not os.listdir(agents_path):
    raise ValueError('The "agents" folder is missing, not a directory, or empty.')

# Iterate over each folder inside the 'agents' folder
for agent_name in os.listdir(agents_path):
    agent_folder = os.path.join(agents_path, agent_name)
    if os.path.isdir(agent_folder):
        # Read contents from the 'instructions.md' file
        instructions = ''
        instructions_file_path = os.path.join(agent_folder, 'instructions.md')
        if os.path.isfile(instructions_file_path):
            with open(instructions_file_path, 'r') as f:
                instructions = f.read()
        
        # Check for the 'files' subfolder and process its contents
        files = []
        files_folder = os.path.join(agent_folder, 'files')
        if os.path.isdir(files_folder):
            for filename in os.listdir(files_folder):
                file_path = os.path.join(files_folder, filename)
                with open(file_path, 'rb') as file_data:
                    # Upload each file to OpenAI
                    file_object = client.files.create(file=file_data, purpose='assistants')
                    files.append({"name": filename, "id": file_object.id})

        print(agent_name)
        print("")
        print(instructions)
        if files:
            print("")
            print(f"Files: {list(map(lambda x: x['name'], files))}")

        create_params = {
            "name": agent_name,
            "instructions": instructions,
            "model": 'gpt-4-1106-preview',
            "tools": [{'type': 'code_interpreter'}, {'type': 'retrieval'}]
        }
        
        # Only include 'file_ids' if there are files
        if files:
            create_params['file_ids'] = list(map(lambda x: x['id'], files))

        # Create the assistant using the uploaded file IDs if files exist
        assistant = client.beta.assistants.create(**create_params)
        print("***********************************************")