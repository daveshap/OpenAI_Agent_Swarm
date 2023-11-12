# from openai import OpenAI
import os
import time
import json
import threading
from ..intercom import intercom
from shared.openai_config import get_openai_client

thread_logs_path = os.getenv('THREAD_LOGS_PATH') or 'logs'
client = get_openai_client()

message_template = '''Chat list:
{chat_list}

Message:
{message}'''

class Agent:
    def __init__(self, id, name, description=None):
        self.id = id
        self.name = name
        self.description = description
        self.messages = []
        self.current_run_id = None
        self.thread = None
        self.last_logged_message_id = None

    def init(self, begin=True):
        self.log('Initializing agent')
        self.init_thread()

        threading.Thread(target=self.run).start()

        if begin:
            self.send_message('Begin')

    def send_message(self, message):
        self.log('Adding message to thread')
        chat_list = '\n'.join([json.dumps(chat) for chat in intercom.get_chat_list_for(self.id)])
        self.messages.append({
            'content': message_template.format(message=message, chat_list=chat_list),
            'role': 'user'
        })

    def init_thread(self):
        self.log('Initializing thread')
        if self.thread is not None:
            return
        
        self.thread = client.beta.threads.create(messages=[])

    def run(self):
        while True:
            if self.current_run_id:
                self.process_current_run()
            elif len(self.messages) > 0:
                self.start_new_run()

            time.sleep(1)

    def process_current_run(self):
        self.log('Waiting for current run to finish')
        run = client.beta.threads.runs.retrieve(thread_id=self.thread.id, run_id=self.current_run_id)
        if run.status == 'queued' or run.status == 'in_progress':
            return

        if run.status == 'completed':
            self.log_thread()
            self.current_run_id = None
            self.log('Completed a run')

        if run.status == 'failed':
            self.current_run_id = None
            raise Exception('Run failed. Run id: {}'.format(run.id))
        
        if run.status == 'expired':
            self.current_run_id = None
            raise Exception('Run expired. Run id: {}'.format(run.id))
        
        if run.status == 'requires_action':
            self.log('Run requires action')
            tool_outputs = []
            for function_call in run.required_action.submit_tool_outputs.tool_calls:
                func_name = function_call.function.name
                self.log('function: {}, params: {}'.format(func_name, function_call.function.arguments))
                try:
                    params = json.loads(function_call.function.arguments)
                except:
                    tool_outputs.append({
                        'tool_call_id': function_call.id,
                        'output': 'Invalid function arguments (Invalid JSON)'
                    })
                    continue


                output = self.process_function_call(func_name, params)

                tool_outputs.append({
                    'tool_call_id': function_call.id,
                    'output': output
                })

            self.log('Submitting tool outputs')
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=self.thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )

    def start_new_run(self):
        self.log('Starting a new run')

        for message in self.messages:
            client.beta.threads.messages.create(
                thread_id=self.thread.id,
                content=message['content'],
                role=message['role']
            )
            
        self.log_thread()
        self.messages = []

        run = client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.id
        )

        self.current_run_id = run.id

    def process_function_call(self, func_name, params):
        if func_name == 'send_message':
            return intercom.send_message(
                message=params['message'],
                receiver_id=params['chat_id'],
                sender_id=self.id
            )
        if func_name == 'create_chat':
            return intercom.create_chat(
                members=params['agent_ids'] + [self.id],
                name=params['name'],
                description=params['description'],
                admin_id=self.id
            )
        if func_name == 'add_chat_member':
            return intercom.add_member_to_chat(
              admin_id=self.id,
              chat_id=params['chat_id'],
              member_id=params['member_id']
            )
        if func_name == 'remove_chat_member':
            return intercom.remove_member_from_chat(
              admin_id=self.id,
              chat_id=params['chat_id'],
              member_id=params['member_id']
            )
        
    def log(self, message):
        print('[{}]: {}'.format(self.name, message))

    def log_thread(self):
        thread_messages = client.beta.threads.messages.list(
            self.thread.id,
            after=self.last_logged_message_id,
            order='asc',
            limit=100
        )

        if not os.path.exists(thread_logs_path):
            os.makedirs(thread_logs_path)

        path = '{}/{}'.format(thread_logs_path, self.name)
        logs = open(path, 'a' if os.path.exists(path) else 'w') 
        for message in thread_messages.data:
            content = '\n'.join([piece.text.value for piece in message.content])
            logs.write('=' * 20 + message.role + ':' + message.id + '=' *  20 + '\n')
            logs.write(content + '\n')
            self.last_logged_message_id = message.id
        
        logs.close()

        if thread_messages.has_more:
            self.log_thread()
