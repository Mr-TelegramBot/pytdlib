import pytdlib
from ...ext import BaseClient


class OnRawUpdate(BaseClient):
    def on_raw_update(self, group: int = 0):
        """Use this decorator to automatically register a function for handling
        raw updates. This does the same thing as :meth:`add_handler` using the
        :class:`RawUpdateHandler`.
        Args:
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func):
            self.add_handler(pytdlib.RawUpdateHandler(func), group)
            return func

        return decorator
