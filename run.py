from google_module.google_module import get
import asyncio
import logging
from check_text.sending_message import sending_messages
from check_text.check_text_from_chat import router_chat
from check_text.check_text_from_user import router_user
from aiogram import Bot, Dispatcher, types
import json
from datetime import date

# Чтение конфига
from config import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# root_logger= logging.getLogger()
# root_logger.setLevel(logging.WARNING) # or whatever
# handler = logging.FileHandler('app.log', 'a', 'utf-8') # or whatever
# handler.setFormatter(logging.Formatter('%(name)s %(message)s - %(asctime)s')) # or whatever
# root_logger.addHandler(handler)



# Объект бота
bot = Bot(token=config["TG_TOKEN"])
# Пришлось создать отдельный объект бота для второго потока
# Диспетчер
dp = Dispatcher()

dp.include_router(router_chat)
dp.include_router(router_user)

# Хэндлер на команду /start
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    # Если в личку боту пишут
    # print(message)
    if message.from_user.id == message.chat.id:
        await sending_messages(text="Привет! Скопируй сообщение ниже и заполни его, после чего вышли заполненное сообщение мне.\n" + 
            "В сообщении слово «Договор­» замените на Ваш договор. «ТК» на Ваш ТК. Прочие поля должны остаться без изменений.\n", message=message)
        
        return await sending_messages(text="Имя:\nПогрузка:\nОткуда:\nКуда:\nВодитель:\nТел:\nПаспорт:\nДата выдачи:\nКем выдан:\nТягач:\nп/п:\nСтавка:\n\nДоговор - ТК", message=message)

    # return await message.answer(f"Привет! Я всё ещё работую.\nПроверка таблиц: {th.is_alive()}")


@dp.message(commands=["repeat"])
async def repeat(message: types.Message):
    # Если в личку боту пишут
    if message.from_user.id == message.chat.id:
        
        return await sending_messages(text="Имя:\nПогрузка:\nОткуда:\nКуда:\nВодитель:\nТел:\nПаспорт:\nДата выдачи:\nКем выдан:\nТягач:\nп/п:\nСтавка:\n\nДоговор - ТК", message=message)


# Запуск процесса поллинга новых апдейтов
async def main():
    while True:
        try:
            await dp.start_polling(bot)
        except:
            await asyncio.sleep(5)


if __name__ == "__main__":
    # Запуск тг бота
    asyncio.run(main())