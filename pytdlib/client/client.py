import getpass
import logging
import threading
from threading import Thread

from pytdlib.session import Session
from .dispatcher import Dispatcher
from .ext import BaseClient
from .methods import Methods

log = logging.getLogger(__name__)


class Client(Methods, BaseClient):
    UPDATES_WORKERS = 1

    def __init__(self,
                 api_id: str = None,
                 api_hash: str = None,
                 auth_value: str = None,
                 workers: int = 4):
        """
        Initialize the variables of class
        """
        super().__init__()

        self.api_id = api_id
        self.api_hash = api_hash
        self.auth_value = auth_value
        self.auth_type = 'user'
        self.workers = workers

        self.dispatcher = Dispatcher(self, workers)

    def start(self):
        """Use this method to start the Client after creating it.
        Requires no parameters.
        Raises:
            :class:`Error <pyrogram.Error>`
        """
        if self.is_started:
            raise ConnectionError("Client has already been started")

        self.session = Session(self)
        self.session.start()
        self.is_started = True

        for i in range(self.UPDATES_WORKERS):
            self.updates_workers_list.append(
                Thread(
                    target=self.updates_worker,
                    name="UpdatesWorker#{}".format(i + 1)
                )
            )

            self.updates_workers_list[-1].start()

        self.dispatcher.start()

    def stop(self):
        """Use this method to manually stop the Client.
        Requires no parameters.
        """
        if not self.is_started:
            raise ConnectionError("Client is already stopped")

        self.dispatcher.stop()

        for i in self.updates_workers_list:
            i.join()

        self.updates_workers_list.clear()

        self.is_started = False

    def add_handler(self, handler, group: int = 0):
        """Use this method to register an update handler.
        You can register multiple handlers, but at most one handler within a group
        will be used for a single update. To handle the same update more than once, register
        your handler using a different group id (lower group id == higher priority).
        Args:
            handler (``Handler``):
                The handler to be registered.
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        Returns:
            A tuple of (handler, group)
        """
        self.dispatcher.add_handler(handler, group)

        return handler, group

    def remove_handler(self, handler, group: int = 0):
        """Removes a previously-added update handler.
        Make sure to provide the right group that the handler was added in. You can use
        the return value of the :meth:`add_handler` method, a tuple of (handler, group), and
        pass it directly.
        Args:
            handler (``Handler``):
                The handler to be removed.
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """
        self.dispatcher.remove_handler(handler, group)

    def updates_worker(self):
        name = threading.current_thread().name
        log.debug("{} started".format(name))

        while True:
            update = self.updates_queue.get()
            try:
                if update:
                    if update['@type'] == 'updateAuthorizationState':
                        self.handle_auth(update)
                    elif update['@type'] == 'error':
                        self.handle_error(update)
                    else:
                        self.dispatcher.updates.put(update)
            except Exception as e:
                log.error(e, exc_info=True)

        log.debug("{} stopped".format(name))

    def handle_auth(self, update):
        if update['authorization_state']['@type'] == 'authorizationStateWaitTdlibParameters':
            log.debug("Received @type=authorizationStateWaitTdlibParameters")
            self.session.send({'@type': 'setTdlibParameters',
                               'parameters': {
                                   '@type': 'tdlibParameters',
                                   'enable_storage_optimizer': True,
                                   'use_message_database': True,
                                   'use_secret_chats': True,
                                   'system_language_code': 'en',
                                   'application_version': '1.0',
                                   'device_model': 'pytdlib',
                                   'system_version': '0.0.1',
                                   'api_id': self.api_id,
                                   'api_hash': self.api_hash,
                                   'database_directory': 'Database',
                                   'files_directory': 'Files'
                               }})
        elif update['authorization_state']['@type'] == 'authorizationStateWaitEncryptionKey':
            log.debug("Received @type=authorizationStateWaitEncryptionKey")
            self.session.send({'@type': 'checkDatabaseEncryptionKey'})
        elif update['authorization_state']['@type'] == 'authorizationStateWaitPhoneNumber':
            log.debug("Received @type=authorizationStateWaitPhoneNumber")
            if self.auth_type is 'user':
                self.session.send({'@type': 'setAuthenticationPhoneNumber',
                              'phone_number': self.auth_value
                              })
            else:
                self.session.send({'@type': 'checkAuthenticationBotToken',
                              'token': self.auth_value
                              })
        elif update['authorization_state']['@type'] == 'authorizationStateWaitCode':
            log.debug("Received @type=authorizationStateWaitCode")
            code = input('Enter code:')
            self.session.send({'@type': 'checkAuthenticationCode', 'code': str(code)})
        elif update['authorization_state']['@type'] == 'authorizationStateWaitPassword':
            log.debug("Received @type=authorizationStateWaitPassword")
            password = getpass.getpass('Password:')
            self.session.send({'@type': 'checkAuthenticationPassword', 'password': password})
        elif update['authorization_state']['@type'] == 'authorizationStateReady':
            log.debug("Received status ready! @type=authorizationStateReady")
            pass

    def handle_error(self, update):
        print(update)
