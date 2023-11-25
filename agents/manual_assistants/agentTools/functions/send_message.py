import os
from function import Function
from logger import AgentLogger


class SendMessage(Function):
    # Ignore for pytest.
    __test__ = False

    def __call__(self, recipient: str, message: str) -> dict:
        """
        Send a message to another agent.

        :param recipient: Agent name to send the message to.
        :type recipient: str
        :param message: Message to send.
        :type message: str
        """
        log = AgentLogger(self.agent.name, self.agent)
        if hasattr(self.agent, 'talksTo') and (recipient in self.agent.talksTo):
            if recipient == "USER":
                log.info(f"Result: {message}", extra={'result': message})
                os._exit(0)
            else:
                log.info(f"[{recipient}] {message}", extra={'recipient': recipient})
                self.context.queues[recipient].put(message)
                return {
                    "tool_call_id": self.context.action.id,
                    "output": f"Message sent to {recipient}"
                }
        else:
            message = f"Unkown recipient {recipient}"
            log.error(message)
            return {
                "tool_call_id": self.context.action.id,
                "output": message
            }
