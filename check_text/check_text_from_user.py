from aiogram import Router, Bot, types
from google_module.google_module import put_info, update_info, get
from google_module.google_config import F_IN_STRING, F_CHECK_IF_IN_STRING, NAME_CHECK, E_CHECK_TK, E_CHECK_IF_IN_STRING_TK
from check_text.sending_message import sending_messages
from datetime import date
import json

# Чтение конфига
from config import config

bt = Bot(token=config["TG_TOKEN"])

router_user = Router()

headers = ["Имя:","Погрузка:", "Откуда:", "Куда:", "Водитель:", "Тел:", "Паспорт:", "Дата выдачи:", "Кем выдан:", "Тягач:", "п/п:", "Ставка:"]

@router_user.message(lambda message: message.from_user.id == message.chat.id and message.content_type=="text")
async def text_handler(message: types.Message):
    """
    Получаем сообщение от пользователя в личку. 
    Пользователь должен прислать по шаблону информацию о поставке.
    После заносим данные в таблицу и отправляем в чат групповой сообщение об этом.
    """
    answer = []

    # Проверки длины
    text = message.text.split("\n")
    if len(text) > 14:
        return await sending_messages(text="Слишком много переносов строк. Скопируйте шаблон и заполните его без добавления новых переносов строк", message=message)
    if len(text) < 14:
        return await sending_messages(text="Вы пропустили каку-то строку для заполнения. Скопируйте шаблон и заполните его без добавления удаления строк", message=message)
    
    # Проверям все ключи
    for i in range(12):
        if headers[i] not in text[i]:
            # print(text[i])
            await sending_messages(text=text[i], message=message)
            return await sending_messages(text="Вы изменили шаблон. Скопируйте шаблон и заполните его без изменений (последнюю строку изменять можно)", message=message)

        text_to_add = text[i][len(headers[i]):].strip()
        if text_to_add == "":
            return await sending_messages(text="Какое-то поле без значения. Скопируйте шаблон и заполните его полностью", message=message)
        
        answer.append(text_to_add)

    # print(answer)
    answer[-3] += " п/п: " + answer[-2]
    del answer[-2]
    # print(answer)

    # Имя
    for i in NAME_CHECK:
        if i in answer[0].lower():
            answer[0] = NAME_CHECK[i]
            break
    else:
        return await sending_messages(text="Имя некорретное", message=message)

    # Если несколько погрузок/откуда, берём первую
    ## Откуда
    answer[2] = answer[2].split(" + ")[0]
    if "(" in answer[2] and ")" in answer[2] and answer[2].index("(") < answer[2].index(")"):
        answer[2] = answer[2][answer[2].index("(")+1:answer[2].index(")")].strip()
    else:
        pass
        # return await sending_messages(text="В «Откуда» проблема", message=message)
    
    # Ищем F по словарям
    F = ""
    if answer[2].lower() in F_IN_STRING:
        F = F_IN_STRING[answer[2].lower()]
    # Если до этого не нашли F
    else:
        for i in F_CHECK_IF_IN_STRING:
            if i in answer[2].lower():
                F = F_CHECK_IF_IN_STRING[i]
                break
    if not F:
        F = answer[2]
        # return await sending_messages(text="«Откуда» не найдено такое", message=message)
    answer[2] = F

    ## Куда
    # answer[3] = answer[3].split(" + ")[0]
    # if "(" in answer[3] and ")" in answer[3] and answer[3].index("(") < answer[3].index(")"):
    #     answer[3] = answer[3][answer[3].index("(")+1:answer[3].index(")")]
    # else:
    #     return await sending_messages(text="В «Куда» проблема", message=message)
    
    # Если договор не разделён с ТК « - »
    if text[-1].count(" - ") != 1:
        return await sending_messages(text="В последней строке три символа « - » должны стоять только между договором и тк. Скопируйте шаблон и заполните его, учитывая эту информацию", message=message)

    ## Договор, тк
    answer += list(map(str.strip, text[-1].split(" - ")))
    
    # Для ТК ищем значение
    TK = ""
    if answer[-1].lower() in E_CHECK_TK:
        TK = E_CHECK_TK[answer[-1].lower()]
    else:
        for i in E_CHECK_IF_IN_STRING_TK:
            if i in answer[-1].lower():
                TK = E_CHECK_IF_IN_STRING_TK[i]
                break
    if TK:
        answer[-1] = TK
    sheet = answer[0]

    answer = [None, None, date.today().strftime('%d.%m.%y'), answer[1], answer[-1], answer[2], answer[4], answer[-4], answer[-2], None, None, None, None, None, None, answer[-3]]

    # Удаляем из ствки скобочки
    if "(" in answer[-1]:
        answer[-1] = answer[-1][:answer[-1].index("(")]

    ## Если несколько договоров
    if answer[8].count(" + ") != 0:
        # Создадим временный список
        pre_answer = [answer[:8] + [i.strip() if "(" not in i else i[:i.index("(")].strip()] + answer[9:] for i in answer[8].split(" + ")]
        answer = pre_answer
    else:
        if "(" in answer[8]:
            answer[8] = answer[8][:answer[8].index("(")].strip()
            
        answer = [answer]

    # Получаем информацию, на какую строку засовывать наши данные
    to_line = get(config["URL_FOR_TABLE_1"], sheet, len_=len(answer))
    if len(to_line) == 1:
        return
    # Засовываем данные
    put_info(answer, sheet, url=config["URL_FOR_TABLE_1"], start_line=to_line[0])

    return await sending_messages(text=message.text + f"\n\nСтроки: {to_line[-1]}", id=config['CHAT_FOR_URL_1'], bt=bt)
