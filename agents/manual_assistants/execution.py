class Execution:
    threadId: str
    runId: str
    actionId: str
    arguments: {}
    exit: bool

    def __init__(self, threadId: str, runId: str, actionId: str, arguments: {}):
        self.threadId = threadId
        self.runId = runId
        self.actionId = actionId
        self.arguments = arguments
        self.exit = False
        
    def __str__(self):
        properties_str = ', '.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f'Execution({properties_str})'
    
    def __repr__(self):
        return self.__str__()