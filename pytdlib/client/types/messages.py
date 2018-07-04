class Messages:
    """This object represents a chat's messages.
    Args:
        total_count (``int``):
            Total number of messages the target chat has.
        messages (List of :obj:`Message <pyrogram.Message>`):
            Requested messages.
    """

    def __init__(self, total_count: int, messages: list):
        self.total_count = total_count  # int
        self.messages = messages
