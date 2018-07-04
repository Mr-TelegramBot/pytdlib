from .on_deleted_messages import OnDeletedMessages
from .on_message import OnMessage
from .on_raw_update import OnRawUpdate


class Decorators(OnDeletedMessages, OnMessage, OnRawUpdate):
    pass
