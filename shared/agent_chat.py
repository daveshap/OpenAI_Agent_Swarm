import time
import json
import os
from . import colorful_cli as cli
from colorama import Fore

class AgentChat:
    
    def __init__ (self, client, thread, assistant, functions):
        self.client = client
        self.thread = thread
        self.assistant = assistant
        self.functions = functions

    def _have_user_chat (self):
        user_message = input(Fore.GREEN + "\nYou: " + Fore.RESET)
        self.client.beta.threads.messages.create(
            self.thread.id,
            role="user",
            content=user_message,
        )
        return user_message
    
    def _have_assistant_respond (self):

        print(f"{Fore.BLUE}\nAssistant Executing:{Fore.RESET}")

        # get assistant response in thread
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id,
        )

        # wait for run to complete
        for i in range(180):

            time.sleep(0.33)
            cli.spinner("Waiting for assistant to respond...")

            if (i % 3) == 0:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread.id,
                    run_id=run.id,
                )

                if run.status == "completed":
                    break
                elif run.status == "in_progress":
                    continue
                elif run.status == "queued":
                    continue
                elif run.status == "requires_action":
                    if run.required_action.type == 'submit_tool_outputs':

                        tool_calls = run.required_action.submit_tool_outputs.tool_calls

                        tool_outputs = []
                        for tc in tool_calls:
                            cli.spinner(f"Running tool {tc.function.name}...")
                            function_to_call = self.functions.get(tc.function.name, None)
                            if not function_to_call:
                                raise ValueError(f"Function {tc.function.name} not found in execution environment")
                            function_args = json.loads(tc.function.arguments)
                            function_response = function_to_call(**function_args)

                            tool_outputs.append({
                                "tool_call_id": tc.id,
                                "output": json.dumps(function_response),
                            })
                            cli.complete(f"Ran tool {tc.function.name}")

                        cli.spinner("Waiting for assistant to respond...")
                        run = self.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=self.thread.id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                else:
                    input(f'unhandled run status: {run.status}. press enter to continue, or ctrl+c to quit')


        # get most recent message from thread
        thread_messages = self.client.beta.threads.messages.list(self.thread.id, limit=10, order='desc')
        assistant_response = thread_messages.data[0].content[0].text.value

        cli.complete("Assistant responded")
        print(f"{Fore.BLUE}\nAssistant: {Fore.RESET}{assistant_response}")

        return assistant_response

        
    def have_fullscreen_convo(self, name=""):
        os.system('clear')
        cli.header(f"Chatting with Assistant {name}")
        print()
        cli.note(f"Can invoke {','.join(self.functions)}")
        print()
        cli.hr()
        print()
        self.have_convo()

    def have_convo(self):
        
        while True:

            # Chat with assistant
            self._have_user_chat()
            self._have_assistant_respond()