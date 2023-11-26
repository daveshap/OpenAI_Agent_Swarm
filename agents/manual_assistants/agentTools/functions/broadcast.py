from function import Function
from logger import AgentLogger


class Broadcast(Function):
    # Ignore for pytest.
    __test__ = False

    def __call__(self, channel_name: str, message: str) -> dict:
        """
        Broadcast a message on a channel.

        :param channel_name: Channel name to broadcast the message to.
        :type channel_name: str
        :param message: Message to broadcast.
        :type message: str
        """
        log = AgentLogger(self.agent.name, self.agent)
        action_id = self.execution.actionId
        if hasattr(self.agent, 'channels') and (channel_name in self.agent.channels):
            for channel in self.context.channels:
                if channel['name'] == channel_name:
                    log.info(f"Action ID {action_id} ({channel_name}) {message}", extra={'broadcast_channel': channel_name, 'action_id': action_id})
                    for recipient in channel['agents']:
                        if recipient != self.agent.name:  # Do not queue the message on the agent that sent in
                            self.context.queues[recipient].put(message)
            return f"Message sent to {channel_name}"
        else:
            message = f"Action ID {action_id} unkown channel {channel_name}"
            log.error(message, extra={'channel': channel_name, 'action_id': action_id})
            return message
