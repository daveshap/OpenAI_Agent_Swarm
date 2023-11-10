from openai import OpenAI
import os
import json

api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("The OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)

request_function_tool = r"""{
  "name": "function_request",
  "description": "request an authority to grant you access to a new function",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "name of the function"
      },
      "description": {
        "type": "string",
        "description": "expected function behaviour"
      },
      "schema": {
        "type": "string",
        "description": "the input arguments for the requested function following the JOSN schema in a format ready to be serialized"
      }
    },
    "required": [
      "name",
      "schema"
    ]
  }
}"""

assistant_package = {
    "model": "gpt-4-1106-preview",
    "description": "assistant to demonstrate tool creation",
    "instructions": """Instruction Set for Assistant-to-be-Tool_Creator:

Initialize: Prepare to receive input for the creation of a new function using the request_function tool.

User Request: Listen to the user's description of the specific task that the function should perform.

Function Name: a. Derived from the task description, formulate a concise and descriptive function name. b. Aim for clarity and specificity to convey the function's purpose effectively.

Function Description: a. Write a clear and precise description of the function's expected behavior. b. Include details about what the function will accomplish and any side effects. c. (Emphasize) Ensure that the description explicitly communicates the function's intended outcome to avoid ambiguity.

Input Arguments JSON Schema: a. Based on the requirements of the task, define the JSON schema for the input arguments. b. The schema should be comprehensive and must specify the types, required fields, and constraints for each input argument. c. Ensure that the schema aligns with the user's requirements and the function's intended behavior.

Validation: Cross-check the name, description, and JSON schema against the user's requirements to confirm accuracy and completeness.

Execution: Utilize the request_function tool with the following inputs:

name: [Function Name]
descriptions: [Function Description]
input_argument_json_schema: [Input Arguments JSON Schema]
Feedback Loop: Promptly present the newly created function specifications to the user for any feedback or necessary revisions.

Iterate: Make adjustments as requested by the user, refining the function name, description, and input argument schema until it meets the user's satisfaction.

Finalize: Once the user gives approval, consider the function creation process complete.

Note: Remember to prioritize user requirements and emphasize clear communication in the function description, as highlighted by the user.""",
    "name": "tool_creator",
}


def tool_from_function_schema(schema):
    """takes a JSON schema and wraps in an OpenAI specified tool structure"""
    tool = f"""{{
    "type":"function",
    "function": {json.dumps(schema)}}}
    """
    tool = json.loads(tool)
    return tool


def schema_from_response(response):
    """Takes an agent response and forms a JSON schema"""
    function_request_obj = json.loads(response)
    name = function_request_obj["name"]
    description = function_request_obj["description"]
    schema = function_request_obj["schema"]
    schema = rf"""{{
  "name": "{name}",
  "description": "{description}",
  "parameters": 
    {schema}
  
}}"""
    return json.loads(schema)


def get_assistant():
    """Retrieve or create an assistant for testing this functionality"""
    if not assistant_package["name"] in [
        assistant.name for assistant in client.beta.assistants.list()
    ]:
        tools = [tool_from_function_schema(request_function_tool)]
        assistant = client.beta.assistants.create(
            model=assistant_package["model"],
            description=assistant_package["description"],
            instructions=assistant_package["instructions"],
            name=assistant_package["name"],
            tools=tools,
        )
    else:
        assistant_dict = {
            assistant.name: assistant.id for assistant in client.beta.assistants.list()
        }
        assistant = client.beta.assistants.retrieve(
            assistant_id=assistant_dict[assistant_package["name"]]
        )
    return assistant


def run_response(run, assistant, thread):
    """Supply context to assistant and await for next user response"""
    while run.status != "completed":
        run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)
        if run.status == "requires_action":
            tools = []
            responses = []
            for call in run.required_action.submit_tool_outputs.tool_calls:
                print(f"calling: {call.function.name}")
                if call.function.name == "function_request":
                    schema = schema_from_response(call.function.arguments)
                    tool = tool_from_function_schema(schema)
                    tools.append(tool)
                responses.append({"tool_call_id": call.id, "output": "{success}"})
            assistant = client.beta.assistants.update(
                assistant_id=assistant.id, tools=[*assistant.tools, *tools]
            )
            run = client.beta.threads.runs.submit_tool_outputs(
                run_id=run.id, thread_id=thread.id, tool_outputs=responses
            )
    print(
        client.beta.threads.messages.list(thread_id=thread.id)
        .data[0]
        .content[0]
        .text.value
    )
    print(
        [
            tool.function.name
            for tool in client.beta.assistants.retrieve(assistant_id=assistant.id).tools
        ]
    )
    return run, assistant


if __name__ == "__main__":
    assistant = get_assistant()
    thread = client.beta.threads.create(
        messages=[{"role": "user", "content": input("Begin\n")}]
    )

    while True:
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="please remember you are talking to an API, minimize output text tokens for cost saving.",
        )
        run, assistant = run_response(run, assistant, thread)
        client.beta.threads.messages.create(
            thread_id=thread.id, content=input("respond: "), role="user"
        )
