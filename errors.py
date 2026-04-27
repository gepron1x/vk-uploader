import loguru
from vkbottle import ErrorHandler
from vkbottle.bot import Message, MessageEvent

error_handler = ErrorHandler(redirect_arguments=True)


@error_handler.register_undefined_error_handler
async def on_error(error: Exception, message: Message | MessageEvent, *args, **kwargs):
    reply_text = "Ошибка. Убедись, что ссылка правильная. "\
                 "Возможно, бот не имеет "\
                 "доступ к ресурсу либо он совсем сломался.\n"\
                 f"{str(error)}"
    if isinstance(message, Message):
        await message.reply(reply_text)
    elif isinstance(message, MessageEvent):
        await message.send_message(reply_text)
    loguru.logger.exception(error)