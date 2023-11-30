from toolStatus import ToolStatus

class Execution:
    threadId: str
    runId: str
    actionId: str
    arguments: {}
    exit: bool
    toolStatus: ToolStatus

    def __init__(self):
        self.exit = False
        self.toolStatus = ToolStatus()
        
    def __str__(self):
        properties_str = ', '.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f'Execution({properties_str})'
    
    def __repr__(self):
        return self.__str__()
    
