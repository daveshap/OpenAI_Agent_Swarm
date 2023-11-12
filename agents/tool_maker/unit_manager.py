from assistant_manager import AssistantManager
from chat_manager import ChatManager


class Unit:
    def __init__(self, client):
        self.assistant_manager = AssistantManager(client=client)
        self.chat_manager = ChatManager(client=client)
        self.interface_assistant = self.assistant_manager.get_assistant()
        self.functional_assistant = self.assistant_manager.get_coding_assistant()

        self.interface_thread = self.chat_manager.create_empty_thread()
        self.functional_thread = self.chat_manager.create_empty_thread()

    def chat(self):
        while True:
            (
                self.interface_assistant,
                self.interface_thread,
                self.functional_thread,
            ) = self.chat_manager.run_unit(
                interface_assistant=self.interface_assistant,
                interface_thread=self.interface_thread,
                functional_assistant=self.functional_assistant,
                functional_thread=self.functional_thread,
            )


if __name__ == "__main__":
    import os
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key is None:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")
    client = OpenAI(api_key=api_key)

    unit = Unit(client=client)
    unit.chat()
