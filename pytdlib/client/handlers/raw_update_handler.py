from .handler import Handler


class RawUpdateHandler(Handler):
    def __init__(self, callback: callable):
        super().__init__(callback)
