class Agent:
    def __init__(self, properties):       
        # Initialize all properties from the dictionary
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