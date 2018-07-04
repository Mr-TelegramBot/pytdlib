class Update:
    """This object represents an incoming update.
    At most one of the optional parameters can be present in any given update.
    Args:
        message (:obj:`Message <pytdlib.Message>`, *optional*):
            New incoming message of any kind — text, photo, sticker, etc.
    """

    def __init__(
            self,
            message=None,
            edited_message=None,
            deleted_messages=None,
            channel_post=None,
            edited_channel_post=None,
            deleted_channel_posts=None,
    ):
        self.message = message
        self.edited_message = edited_message
        self.deleted_messages = deleted_messages
        self.channel_post = channel_post
        self.edited_channel_post = edited_channel_post
        self.deleted_channel_posts = deleted_channel_posts
