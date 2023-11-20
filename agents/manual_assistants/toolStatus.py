class ToolStatus:
    waiting: bool
    output: {}

    def __init__(self):
        self.waiting = False
        self.output = {}
        
    def __str__(self):
        properties_str = ', '.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f'Execution({properties_str})'
    
    def __repr__(self):
        return self.__str__()
    