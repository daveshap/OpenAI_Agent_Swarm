import importlib
from pathlib import Path
from agents.tool_maker.tool_manager import ToolManager
import json
import os
from openai import OpenAI

Assistant = type(OpenAI().beta.assistants.list().data[0])
Thread = type(OpenAI().beta.threads.create())


class ChatManager:
    def __init__(self, client: OpenAI):
        self.client = client
        functions_path = os.path.join(
            Path(__file__).absolute().parent, "python_functions"
        )
        self.functions_path = functions_path
        print(self.functions_path)

    def create_thread_from_user_input(self):
        return self.client.beta.threads.create(
            messages=[{"role": "user", "content": input("Begin\n")}]
        )

    def create_empty_thread(self):
        return self.client.beta.threads.create()

    def run_python_from_function_name(self, call):
        print("CALLING FUNCTION")
        base = ".".join(__name__.split(".")[:-1])
        try:
            function_name = call.function.name

            fn = getattr(
                importlib.reload(
                    importlib.import_module(f"{base}.python_functions.{function_name}")
                ),
                function_name,
            )
            print(fn)
            result = fn(**json.loads(call.function.arguments))
            response = {"tool_call_id": call.id, "output": f"result:{result}"}
        except Exception as error:
            response = {
                "tool_call_id": call.id,
                "output": f"{{{type(error)}:{error.args}}}",
            }
        print(response)
        return response
    
    def get_existing_functions(self):
        print("Get Built Functions")
        results = []
        if os.path.exists(self.functions_path):
            for filename in os.listdir(self.functions_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.functions_path,filename)
                    with open(file_path, "r") as file:
                        results.append(file)
        return results

    def handle_fucntion_request(
        self,
        call,
        interface_assistant: Assistant,
        interface_thread: Thread,
        functional_assistant: Assistant,
        functional_thread: Thread,
    ):
        try:
            # Create Function Tool
            schema = ToolManager.schema_from_response(call.function.arguments)
            tool = ToolManager.tool_from_function_schema(schema)
            filtered_interface_assistant_tools = list(filter(lambda tool: tool.type == "function" ,interface_assistant.tools))
            if tool["function"]["name"] in [
                previous_tool.function.name
                for previous_tool in filtered_interface_assistant_tools
            ]:
                tools = [
                    previous_tool
                    for previous_tool in filtered_interface_assistant_tools
                    if previous_tool.function.name != tool["function"]["name"]
                ]
                interface_assistant = self.client.beta.assistants.update(
                    assistant_id=interface_assistant.id,
                    tools=[*tools, tool],
                )
            else:
                interface_assistant = self.client.beta.assistants.update(
                    assistant_id=interface_assistant.id,
                    tools=[*interface_assistant.tools, tool],
                )

            # Generate Python Function
            self.client.beta.threads.messages.create(
                thread_id=functional_thread.id, content=str(tool), role="user"
            )
            functional_run = self.client.beta.threads.runs.create(
                thread_id=functional_thread.id,
                assistant_id=functional_assistant.id,
            )
            
            functional_response = self.simple_run(
                run=functional_run,
                thread=functional_thread,
            )
            function_lines = functional_response.split("```python")[1].split("```")[0]
            name = tool["function"]["name"]
            if not os.path.exists(self.functions_path):
                os.mkdir(self.functions_path)
            with open(f"{self.functions_path}/{name}.py", "w") as file:
                file.writelines(function_lines)
            with open(f"{self.functions_path}/{name}.json", "w") as file:
                file.writelines(str(schema))

            response = {"tool_call_id": call.id, "output": "{success}"}

        except Exception as error:
            # If error, pass details back to assistant for next steps
            response = {
                "tool_call_id": call.id,
                "output": f"{{{type(error)}:{error.args}}}",
            }

        return interface_assistant, response

    def simple_run(self, run, thread):
        """Supply context to assistant and await for next user response"""
        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                run_id=run.id, thread_id=thread.id
            )
            if run.status == "requires_action":
                responses = []
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    print(f"calling: {call.function.name}")
                    if call.function.name == "get_existing_functions":
                        available_functions = self.get_existing_functions()
                        response = {"tool_call_id": call.id, "output": f"result:{available_functions}"}
                        responses.append(response)
                    else:
                        response = {"tool_call_id": call.id, "output": f"result:None"}
                        responses.append(response)
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        run_id=run.id,
                        thread_id=thread.id,
                        tool_outputs=responses,
                    )
                except:
                    print(run.status)
                    print(run)
                    print(call)
                    print(responses)

        response = (
            self.client.beta.threads.messages.list(thread_id=thread.id)
            .data[0]
            .content[0]
            .text.value
        )
        return response

    def begin_run(
        self,
        run,
        interface_assistant,
        interface_thread,
        functional_assistant,
        functional_thread,
    ):
        while run.status != "completed":
            run = self.client.beta.threads.runs.retrieve(
                run_id=run.id, thread_id=interface_thread.id
            )
            if run.status == "requires_action":
                tools = []
                responses = []
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    print(f"calling: {call.function.name}")
                    if call.function.name == "function_request":
                        interface_assistant, response = self.handle_fucntion_request(
                            call=call,
                            interface_assistant=interface_assistant,
                            interface_thread=interface_thread,
                            functional_assistant=functional_assistant,
                            functional_thread=functional_thread,
                        )
                    else:
                        response = self.run_python_from_function_name(call)
                    responses.append(response)
                try:
                    run = self.client.beta.threads.runs.submit_tool_outputs(
                        run_id=run.id,
                        thread_id=interface_thread.id,
                        tool_outputs=responses,
                    )
                except:
                    print(run.status)
                    print(run)
                    print(call)
                    print(responses)
            if run.status == "failed" or run.status == "expired":
                print("DIED")
                run.status = "completed"
        response = (
            self.client.beta.threads.messages.list(thread_id=interface_thread.id)
            .data[0]
            .content[0]
            .text.value
        )
        return interface_assistant, response

    def run_unit(
        self,
        interface_assistant: Assistant,
        interface_thread: Thread,
        functional_assistant: Assistant,
        functional_thread: Thread,
    ):
        self.client.beta.threads.messages.create(
            thread_id=interface_thread.id, content=input("type: "), role="user"
        )
        print()
        interface_run = self.client.beta.threads.runs.create(
            thread_id=interface_thread.id,
            assistant_id=interface_assistant.id,
            instructions="please remember you are talking to an API, minimize output text tokens for cost saving. You are also able to communicate with the function ai using the description property of function_request.",
        )
        interface_assistant, response = self.begin_run(
            run=interface_run,
            interface_assistant=interface_assistant,
            interface_thread=interface_thread,
            functional_assistant=functional_assistant,
            functional_thread=functional_thread,
        )
        interface_thread = self.client.beta.threads.retrieve(
            thread_id=interface_thread.id
        )
        functional_thread = self.client.beta.threads.retrieve(
            thread_id=functional_thread.id
        )
        print(response)
        print()
        return interface_assistant, interface_thread, functional_thread
