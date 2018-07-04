from pytdlib.client import types as pytdlib_types


def parse_message(
        message,
        is_edited_message: bool
) -> pytdlib_types.Message:
    if is_edited_message:
        m = pytdlib_types.Message(
            message_id=message['message_id'],
            chat=parse_chat(message['chat_id']),
            edited=True,
            text=message['new_content']['text']['text']
        )
    else:
        new_message = message['message']
        m = pytdlib_types.Message(
            message_id=new_message['id'],
            chat=parse_chat(new_message['chat_id']),
            edited=False,
            text=new_message['content']['text']['text']
        )

    return m


def parse_deleted_messages(
        message_ids: list,
        chat_id: int
) -> pytdlib_types.Messages:
    parsed_messages = []

    for message in message_ids:
        parsed_messages.append(
            pytdlib_types.Message(
                message_id=message,
                chat=parse_chat(chat_id)
            )
        )

    return pytdlib_types.Messages(len(parsed_messages), parsed_messages)


def parse_chat(chat_id: int) -> pytdlib_types.Chat:
    if chat_id is None:
        return None
    return pytdlib_types.Chat(id=chat_id, type=get_type_chat(chat_id))


def get_type_chat(
        chat_id: int
) -> str:
    if str(chat_id).startswith('-100'):
        return pytdlib_types.ChatType.CHANNEL
    elif str(chat_id).startswith('-'):
        return pytdlib_types.ChatType.BASIC_GROUP
    else:
        return pytdlib_types.ChatType.PRIVATE
