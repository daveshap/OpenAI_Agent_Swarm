from function import Function
from logger import AgentLogger


class AssignTask(Function):
    # Ignore for pytest.
    __test__ = False

    def __call__(self, assignee: str, task: str) -> None:
        """
        Assign a task to the worker agents.

        :param assignee: Name of the agent assigned to this task.
        :type assignee: str
        :param task: Description of the task.
        :type task: str
        """
        log = AgentLogger(self.agent.name, self.agent)
        action_id = self.execution.actionId
        log.info(f"[ASSIGN TASK {action_id}]>[{assignee}] {task}", extra={'action_id': action_id, 'task': task, 'assignee': assignee})
        self.execution.toolStatus.waiting = True
        self.context.queues[assignee].put(f"Task id: {action_id}\n{task}")
