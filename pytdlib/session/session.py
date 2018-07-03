import json
import logging
import threading
import time
from ctypes import *
from datetime import datetime
from threading import Thread

log = logging.getLogger(__name__)


class Session:
    NET_WORKERS = 1
    MAX_RETRIES = 5

    def __init__(self, client):
        self.tdclient = None
        self.client = client
        self.net_worker_list = []
        self._init()

    def start(self):
        while True:
            try:
                for i in range(self.NET_WORKERS):
                    self.net_worker_list.append(
                        Thread(
                            target=self.net_worker,
                            name="NetWorker#{}".format(i + 1)
                        )
                    )
                    self.net_worker_list[-1].start()
            except Exception as e:
                log.error(e, exc_info=True)
                raise e
            else:
                break

        log.debug("Session started")

    def stop(self):
        for i in self.net_worker_list:
            i.join()

        self.net_worker_list.clear()

        log.debug("Session stopped")

    def net_worker(self):
        name = threading.current_thread().name
        log.debug("{} started".format(name))

        while True:
            try:
                update = self._receive()
                if self.client is not None:
                    self.client.updates_queue.put(update)
            except Exception as e:
                log.error(e, exc_info=True)
                break

        log.debug("RecvThread stopped")

    def send(self, data, retries: int = MAX_RETRIES):
        try:
            return self._send(data)
        except Exception as e:
            if retries == 0:
                raise e from None

            (log.warning if retries < 3 else log.info)(
                "{}: {} Retrying {}".format(
                    Session.MAX_RETRIES - retries,
                    datetime.now(), type(data)))

            time.sleep(0.5)
            return self.send(data, retries - 1)

    def _init(self):
        """
        Initialize a new instance of TDLib.
        """
        tdjson = CDLL("/home/CIT/mateusc/projects/mv/pytdlib/pytdlib/lib/libtdjson.so")

        # load TDLib functions from shared library
        td_json_client_create = tdjson.td_json_client_create
        td_json_client_create.restype = c_void_p
        td_json_client_create.argtypes = []

        self.td_json_client_receive = tdjson.td_json_client_receive
        self.td_json_client_receive.restype = c_char_p
        self.td_json_client_receive.argtypes = [c_void_p, c_double]

        self.td_json_client_send = tdjson.td_json_client_send
        self.td_json_client_send.restype = None
        self.td_json_client_send.argtypes = [c_void_p, c_char_p]

        self.td_json_client_execute = tdjson.td_json_client_execute
        self.td_json_client_execute.restype = c_char_p
        self.td_json_client_execute.argtypes = [c_void_p, c_char_p]

        td_json_client_destroy = tdjson.td_json_client_destroy
        td_json_client_destroy.restype = None
        td_json_client_destroy.argtypes = [c_void_p]

        td_set_log_file_path = tdjson.td_set_log_file_path
        td_set_log_file_path.restype = c_int
        td_set_log_file_path.argtypes = [c_char_p]

        td_set_log_max_file_size = tdjson.td_set_log_max_file_size
        td_set_log_max_file_size.restype = None
        td_set_log_max_file_size.argtypes = [c_longlong]

        td_set_log_verbosity_level = tdjson.td_set_log_verbosity_level
        td_set_log_verbosity_level.restype = None
        td_set_log_verbosity_level.argtypes = [c_int]

        fatal_error_callback_type = CFUNCTYPE(None, c_char_p)

        td_set_log_fatal_error_callback = tdjson.td_set_log_fatal_error_callback
        td_set_log_fatal_error_callback.restype = None
        td_set_log_fatal_error_callback.argtypes = [fatal_error_callback_type]

        td_set_log_verbosity_level(2)
        c_on_fatal_error_callback = fatal_error_callback_type(self._on_fatal_error_callback)
        td_set_log_fatal_error_callback(c_on_fatal_error_callback)

        # create client
        self.tdclient = td_json_client_create()

    def _receive(self, timeout: c_double = 10.0):
        """
        Receives incoming updates and request responses from the TDLib client.
        :param timeout: Maximum number of seconds allowed for this function to wait for new data.
        :return: parsed dict or None if the timeout expires.
        """
        if self.tdclient is None:
            return Exception
        result = self.td_json_client_receive(self.tdclient, timeout)
        if result:
            result = json.loads(result.decode("utf-8"))
        return result

    def _send(self, data):
        """
        Sends request to the TDLib client.
        :param query:
        :return:
        """
        data = json.dumps(data).encode('utf-8')
        self.td_json_client_send(self.tdclient, data)

    @staticmethod
    def _on_fatal_error_callback(error_message):
        print('TDLib fatal error: ', error_message)
