class Agent:
    # From OAI assistant's API
    name: str
    id: str
    instructions: str
    tools: list[str]
    model: str
    
    # Custom
    talksTo: list[str]
    channels: list[str]
    initMessage: str
 
    def __init__(self, properties):
        # Set default values
        self.model="gpt-4-1106-preview"

        # Overwrite with provided values from YAML
        for key, value in properties.items():
            setattr(self, key, value)

    def __str__(self):
        properties_str = ', '.join(f'{key}: {value}' for key, value in self.__dict__.items())
        return f'Agent({properties_str})'
    
    def __repr__(self):
        return self.__str__()
    
    def update(self, **kwargs):
        # Update properties with new values
        for key, value in kwargs.items():
            setattr(self, key, value)