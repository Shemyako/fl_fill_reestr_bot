import asyncio
from aiogram.exceptions import AiogramError, TelegramForbiddenError
from aiogram.types import FSInputFile
import logging

# Если вдруг ошибки, что б сообщение точно отправилось
# Может остановить поток
async def sending_messages(id:int=None, text:str=None, message=None, bt=None, filename=None):
    while True:
        try:
            if not message and not filename:
                await bt.send_message(id, text) # , parse_mode="HTML")
            elif not message:       # Отправляем файл через bt:
                agenda = FSInputFile(f"{filename}")
                await bt.send_document(id, agenda)
            else:
                await message.answer(text)
            break
        except TelegramForbiddenError as e:
            logging.warning(e)
            break
        except  AiogramError as e:
            logging.warning(e)
            await asyncio.sleep(20)