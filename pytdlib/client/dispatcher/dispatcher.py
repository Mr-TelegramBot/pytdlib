import logging
import threading
from collections import OrderedDict
from queue import Queue
from threading import Thread

import pytdlib
from ..ext import utils
from ..handlers import RawUpdateHandler, MessageHandler, DeletedMessagesHandler

log = logging.getLogger(__name__)


class Dispatcher:
    NEW_MESSAGE_UPDATES = (
        'updateNewMessage'
    )

    EDITED_MESSAGE_UPDATES = (
        'updateMessageContent'
    )

    DELETE_MESSAGE_UPDATES = (
        'updateDeleteMessages'
    )

    MESSAGE_UPDATES = NEW_MESSAGE_UPDATES + EDITED_MESSAGE_UPDATES

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
                else:
                    message = (update.message
                               or update.channel_post
                               or update.edited_message
                               or update.edited_channel_post)

                    deleted_messages = update.deleted_messages

                    if message and isinstance(handler, MessageHandler):
                        if not handler.check(message):
                            continue

                        args = (self.client, message)
                    elif deleted_messages and isinstance(handler, DeletedMessagesHandler):
                        if not handler.check(deleted_messages):
                            continue

                        args = (self.client, deleted_messages)
                    else:
                        continue

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
                self.dispatch(update, is_raw=True)

                if update['@type'] in Dispatcher.MESSAGE_UPDATES:
                    is_edited_message = update['@type'] in Dispatcher.EDITED_MESSAGE_UPDATES

                    message = utils.parse_message(
                        message=update,
                        is_edited_message=is_edited_message
                    )

                    self.dispatch(
                        pytdlib.Update(
                            message=((message if message.chat.type != pytdlib.ChatType.CHANNEL else None)
                                     if not is_edited_message else None),
                            edited_message=((message if message.chat.type != pytdlib.ChatType.CHANNEL else None)
                                            if is_edited_message else None),
                            channel_post=((message if message.chat.type == pytdlib.ChatType.CHANNEL else None)
                                          if not is_edited_message else None),
                            edited_channel_post=((message if message.chat.type == pytdlib.ChatType.CHANNEL else None)
                                                 if is_edited_message else None)
                        )
                    )
                elif update['@type'] in Dispatcher.DELETE_MESSAGE_UPDATES:
                    is_channel = utils.get_type_chat(update['chat_id']) is pytdlib.ChatType.CHANNEL

                    messages = utils.parse_deleted_messages(
                        message_ids=update['message_ids'],
                        chat_id=update['chat_id']
                    )

                    self.dispatch(
                        pytdlib.Update(
                            deleted_messages=(messages if not is_channel else None),
                            deleted_channel_posts=(messages if is_channel else None)
                        )
                    )
                else:
                    continue
            except Exception as e:
                log.error(e, exc_info=True)

        log.debug("{} stopped".format(name))
