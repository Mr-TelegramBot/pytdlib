import pytdlib
from ...ext import BaseClient


class OnDeletedMessages(BaseClient):
    def on_deleted_messages(self, filters=None, group: int = 0):
        """Use this decorator to automatically register a function for handling
        deleted messages. This does the same thing as :meth:`add_handler` using the
        :class:`DeletedMessagesHandler`.
        Args:
            filters (:obj:`Filters <pyrogram.Filters>`):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func):
            self.add_handler(pytdlib.DeletedMessagesHandler(func, filters), group)
            return func

        return decorator
