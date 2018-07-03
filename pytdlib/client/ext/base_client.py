from queue import Queue


class BaseClient:
    def __init__(self):
        self.client = None
        self.session = None
        self.is_started = None
        self.updates_queue = Queue()
        self.updates_workers_list = []

    def send(self, data):
        pass

    def resolve_peer(self, peer_id: int or str):
        pass

    def add_handler(self, handler, group: int = 0) -> tuple:
        pass
