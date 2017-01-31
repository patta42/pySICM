class OutputSignal(object):
    channel = None
    name = None
    
    def __init__(self, name, channel):
        self.channel = channel
        self.name = name
