import time
import json

def chat(client, thread, assistant, functions):
    while True:
        user_message = input("You: ")

        # add user message to thread
        thread_message = client.beta.threads.messages.create(
          thread.id,
          role="user",
          content=user_message,
        ) 

        # get assistant response in thread
        run = client.beta.threads.runs.create(
          thread_id=thread.id,
          assistant_id=assistant.id,
        )

        # wait for run to complete
        wait_time = 0
        while True:
            if wait_time % 5 == 0:
                print(f"waiting for run to complete...", flush=True)
            wait_time += 1
            time.sleep(1)

            run = client.beta.threads.runs.retrieve(
              thread_id=thread.id,
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
                        function_to_call = functions.get(tc.function.name, None)
                        if not function_to_call:
                            raise ValueError(f"Function {tc.function.name} not found in execution environment")
                        function_args = json.loads(tc.function.arguments)
                        function_response = function_to_call(**function_args)

                        tool_outputs.append({
                            "tool_call_id": tc.id,
                            "output": json.dumps(function_response),
                        })

                    print(f"Submitting tool outputs...", flush=True)
                    run = client.beta.threads.runs.submit_tool_outputs(
                      thread_id=thread.id,
                      run_id=run.id,
                      tool_outputs=tool_outputs
                    )
            else:
                input(f'Run status: {run.status}. press enter to continue, or ctrl+c to quit')

        # get most recent message from thread
        thread_messages = client.beta.threads.messages.list(thread.id, limit=10, order='desc')

        # get assistant response from message
        assistant_response = thread_messages.data[0].content[0].text.value

        print(f"\n\nBot: {assistant_response}\n\n", flush=True)

        # continue?
        try:
            input("Press enter to continue chatting, or ctrl+c to stop chat\n")
        except KeyboardInterrupt:
            print(f"Stopping chat\n" + 90*"-" + "\n\n", flush=True)
            break