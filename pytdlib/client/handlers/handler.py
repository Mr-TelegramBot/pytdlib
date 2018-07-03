class Handler:
    def __init__(self, callback: callable, filters=None):
        self.callback = callback
        self.filters = filters
