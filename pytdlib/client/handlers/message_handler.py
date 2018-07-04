from .handler import Handler


class MessageHandler(Handler):
    """The Message handler class. Used to handle text, media and service messages coming from
    any chat (private, group, channel). It is intended to be used with
    :meth:`add_handler() <pyrogram.Client.add_handler>`
    For a nicer way to register this handler, have a look at the
    :meth:`on_message() <pyrogram.Client.on_message>` decorator.
    Args:
        callback (``callable``):
            Pass a function that will be called when a new Message arrives. It takes *(client, message)*
            as positional arguments (look at the section below for a detailed description).
        filters (:obj:`Filters <pyrogram.Filters>`):
            Pass one or more filters to allow only a subset of messages to be passed
            in your callback function.
    Other parameters:
        client (:obj:`Client <pyrogram.Client>`):
            The Client itself, useful when you want to call other API methods inside the message handler.
        message (:obj:`Message <pyrogram.Message>`):
            The received message.
    """

    def __init__(self, callback: callable, filters=None):
        super().__init__(callback, filters)

    def check(self, message):
        return (
            self.filters(message)
            if self.filters
            else True
        )
