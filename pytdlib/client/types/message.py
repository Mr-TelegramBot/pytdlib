class Message:
    """This object represents a message.
    """

    def __init__(
            self,
            message_id: int,
            chat=None,
            text: str = None,
            edited: bool = None
    ):
        self.message_id = message_id  # int
        self.chat = chat  # Chat
        self.text = text
        self.edited = edited
