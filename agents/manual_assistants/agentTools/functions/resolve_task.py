from function import Function
from logger import AgentLogger


class ResolveTask(Function):
    # Ignore for pytest.
    __test__ = False

    def __call__(self, id: str, result: str) -> dict:
        """
        Send final task results to the boss agent.

        :param id: Task id provided when the task was assigned.
        :type id: str
        :param result: Result of the task.
        :type result: str
        """
        log = AgentLogger(self.agent.name, self.agent)
        action_id = self.execution.actionId
        log.info(f"[RESOLVE TASK {id}] {result}", extra={'result': result})
        outputs = []
        outputs.append({
            "tool_call_id": id,
            "output": result,
        })
        for pendingAction in self.context.pendingActions:
            if pendingAction['id'] == id:
                pendingAction['outout'] = outputs
        self.execution.exit = True
        return {
            "tool_call_id": action_id,
            "output": f"Task {id} resolved"
        }
