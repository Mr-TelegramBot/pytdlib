import pytdlib
from ...ext import BaseClient


class OnMessage(BaseClient):
    def on_message(self, filters=None, group: int = 0):
        """Use this decorator to automatically register a function for handling
        messages. This does the same thing as :meth:`add_handler` using the
        :class:`MessageHandler`.
        Args:
            filters (:obj:`Filters <pyrogram.Filters>`):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func):
            self.add_handler(pytdlib.MessageHandler(func, filters), group)
            return func

        return decorator
