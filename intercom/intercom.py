import uuid
import intercom.agent_registry.registry as registry

message_template = '''===Incoming message from {chat_name}===
chat_id: {chat_id}
type: {type}
author_name: {author_name}
author_id: {author_id}
message_content: 
{message}
===End of Incoming message from {chat_name}==='''

class IntercomService:
    def __init__(self):
        self.chats = {}

    def send_message(self, message, receiver_id, sender_id):
        reciever = registry.get_agent(receiver_id) or self.chats[receiver_id]
        sender_agent = registry.get_agent(sender_id)
        self.log('Sending message: {} -> {}'.format(sender_agent.name, reciever.name))

        is_group_chat = isinstance(reciever, Chat)
        message = message_template.format(
            reciever_name=reciever.name,
            chat_id=reciever.id if is_group_chat else sender_agent.id,
            type='group' if is_group_chat else 'agent',
            chat_name=reciever.name if is_group_chat else sender_agent.name,
            author_name=sender_agent.name,
            author_id=sender_agent.id,
            message=message
        )

        if is_group_chat:
            reciever.send_message(message, sender_id)
        else:
            reciever.send_message(message)

        return 'Message was sent successfully. You will be notified when the agent responds.'
    
    def create_chat(self, members, name, description, admin_id):
        if len(members) <= 2:
            return 'Chat must have more than 2 members. Use send_message function for one-to-one communication.'
        
        chat = Chat(members, name, description, admin_id)
        self.chats[chat.id] = chat

        return 'Group chat was created successfully. Group chat id: {}'.format(chat.id)
    
    def add_member_to_chat(self, admin_id, chat_id, member_id):
        if chat_id not in self.chats:
            return 'Chat with id {} does not exist.'.format(chat_id)
        
        chat = self.chats[chat_id]

        if admin_id != chat.admin_id:
            return 'Only admin can add members to the chat.'
        
        chat.add_member(member_id)

        return 'Member was added successfully.'
    
    def remove_member_from_chat(self, admin_id, chat_id, member_id):
        if chat_id not in self.chats:
            return 'Chat with id {} does not exist.'.format(chat_id)
        
        chat = self.chats[chat_id]

        if admin_id != chat.admin_id:
            return 'Only admin can remove members from the chat.'
        
        chat.remove_member(member_id)

        return 'Member was removed successfully.'
    
    def get_chat_list_for(self, agent_id):
        agents = [{
            "id": agent.id,
            "name": agent.name,
            "description": agent.description,
            "type": "agent"
        } for agent in registry.get_agents() if agent.id != agent_id]

        group_chats = [{
            "id": chat.id,
            "name": chat.name,
            "description": chat.description,
            "type": "group"
        } for chat in self.chats.values() if agent_id in chat.members]

        return agents + group_chats
    
    def log(self, message):
        print('[intercom]: {}'.format(message))


class Chat:
    def __init__(self, members, name, description, admin_id):
        self.id = str(uuid.uuid4())
        self.admin_id = admin_id
        self.members = set(members)
        self.name = name
        self.description = description

    def send_message(self, message, sender_id):
        for member in self.members:
            if member == sender_id:
                continue
            agent = registry.get_agent(member)
            agent.send_message(message)

    def add_member(self, member_id):
        self.members.add(member_id)

    def remove_member(self, member_id):
        self.members.remove(member_id)


intercom = IntercomService()