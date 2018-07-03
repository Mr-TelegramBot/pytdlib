import logging
import threading
from collections import OrderedDict
from queue import Queue
from threading import Thread

from ..handlers import RawUpdateHandler

log = logging.getLogger(__name__)


class Dispatcher:
    def __init__(self, client, workers):
        self.client = client
        self.workers = workers
        self.workers_list = []
        self.updates = Queue()
        self.groups = OrderedDict()

    def start(self):
        for i in range(self.workers):
            self.workers_list.append(
                Thread(
                    target=self.update_worker,
                    name="UpdateWorker#{}".format(i + 1)
                )
            )

            self.workers_list[-1].start()

    def stop(self):
        for _ in range(self.workers):
            self.updates.put(None)

        for i in self.workers_list:
            i.join()

        self.workers_list.clear()

    def add_handler(self, handler, group: int):
        if group not in self.groups:
            self.groups[group] = []
            self.groups = OrderedDict(sorted(self.groups.items()))

        self.groups[group].append(handler)

    def remove_handler(self, handler, group: int):
        if group not in self.groups:
            raise ValueError("Group {} does not exist. "
                             "Handler was not removed.".format(group))
        self.groups[group].remove(handler)

    def dispatch(self, update, is_raw: bool = False):
        for group in self.groups.values():
            for handler in group:
                if is_raw:
                    if not isinstance(handler, RawUpdateHandler):
                        continue
                    args = (self.client, update)

                handler.callback(*args)
                break

    def update_worker(self):
        name = threading.current_thread().name
        log.debug("{} started".format(name))

        while True:
            update = self.updates.get()

            if update is None:
                break

            try:
                # print(update)
                self.dispatch(update, is_raw=True)
            except Exception as e:
                log.error(e, exc_info=True)

        log.debug("{} stopped".format(name))
