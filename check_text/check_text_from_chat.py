from aiogram import Router, Bot, types
from google_module.google_module import put_info, update_info, get, del_lines_g
from google_module.google_config import F_IN_STRING, F_CHECK_IF_IN_STRING, NAME_CHECK, E_CHECK_TK, E_CHECK_IF_IN_STRING_TK, SHEETS_ID
from check_text.sending_message import sending_messages
from check_text.parse_message import parse_message_text
import json
from order_module.create_order import get_order

# Чтение конфига
from config import config

bt = Bot(token=config["TG_TOKEN"])

router_chat = Router()

def del_lines(message):
    reply_message = message.reply_to_message
    reply_message = reply_message.text.split("\n")[-1][reply_message.text.split("\n")[-1].index("'")-1:].strip()

    line_amount = reply_message[reply_message.index("!")+1:]
    # Номер начальной строки
    line_num = line_amount[:line_amount.index("-")]
    # Количество линий, которое было раньше
    line_amount = int(line_amount[line_amount.index("-")+1:]) - int(line_amount[:line_amount.index("-")]) + 1

    to_line = get(config["URL_FOR_TABLE_1"], reply_message[:reply_message.index("!")], line_num=line_num)

    del_lines_g(SHEETS_ID[reply_message[:reply_message.index("!")]], start_line=to_line[0], line_amount=line_amount, url=config["URL_FOR_TABLE_1"])




@router_chat.message(lambda message: config["CHAT_FOR_URL_1"] == message.chat.id and message.content_type=="text" and message.reply_to_message)
async def answer_handler(message: types.Message):
    """
    Получаем ответ на сообщение из группового чата. 
    Либо отмена погрузки (удаляем строки из таблицы)
    Либо создание доверенности
    Либо изменение данных о погрузке
    """
    text = list(map(str.strip, message.text.split("\n")))
    if text[0].lower().strip() == "отмена погрузки":
        return del_lines(message)
    elif text[0].lower().strip()[:3] == "от " or text[0].lower().strip()[:15] == "доверенность от":
        return await get_order(message, bt)
    elif text[0].lower().strip() not in ["изменение", "изменения", "изменить"]:
        return

    # Парсим начальное сообщение
    data = parse_message_text(message)

    answer = {
        "имя:":None,"погрузка:":None, "откуда:":None, "куда:":None, "водитель:":None, "тел:":None, "паспорт:":None, 
        "дата выдачи:":None, "кем выдан:":None, "тягач:":None, "п/п:":None, "ставка:":None, "договор:":None, "тк:": None
    }
    # Лист, который изменять будем
    reply_message = message.reply_to_message
    reply_message = reply_message.text.split("\n")[-1][reply_message.text.split("\n")[-1].index("'"):]

    line_amount = reply_message[reply_message.index("!")+1:]
    # Номер начальной строки
    line_num = line_amount[:line_amount.index("-")]
    # Количество линий, которое было раньше
    line_amount = int(line_amount[line_amount.index("-")+1:]) - int(line_amount[:line_amount.index("-")]) + 1

    for i in text[1:]:
        if i == "" or ":" not in i or i[:i.index(":")+1].lower() not in answer:
            # print(i)
            return
        
        answer[i[:i.index(":")+1].lower()] = i[i.index(":")+1:].strip()


    # Формируем сообщение, которое будем изменять. Чтобы в чате была актуальная информация
    message_to_edit = ""
    for i in data:
        if i.lower() in answer and answer[i.lower()]:
            data[i] = answer[i.lower()]
        message_to_edit += f"{i} {data[i]}\n"
    

    # print(answer)
    if answer["тягач:"] and answer["п/п:"]:
        answer["тягач:"] += " п/п: " + answer["п/п:"]
    

    # Если несколько погрузок/откуда, берём первую
    ## откуда
    if answer["откуда:"]:
        answer["откуда:"] = answer["откуда:"].split(" + ")[0]
        if "(" in answer["откуда:"] and ")" in answer["откуда:"] and answer["откуда:"].index("(") < answer["откуда:"].index(")"):
            answer["откуда:"] = answer["откуда:"][answer["откуда:"].index("(")+1:answer["откуда:"].index(")")].strip()
        else:
            ###
            # Ошибка при заполнении откуда
            ###
            pass

        # Ищем F по словарям
        F = ""
        if answer["откуда:"].lower() in F_IN_STRING:
            F = F_IN_STRING[answer["откуда:"].lower()]
        # Если до этого не нашли F
        else:
            for i in F_CHECK_IF_IN_STRING:
                if i in answer["откуда:"].lower():
                    F = F_CHECK_IF_IN_STRING[i]
                    break
        if not F:
            # print(answer["откуда:"])
            F = answer["откуда:"]
            # return await sending_messages(text="«откуда» не найдено такое", message=message)
        answer["откуда:"] = F

    # ## Куда
    # answer[3] = answer[3].split(" + ")[0]
    # if "(" in answer[3] and ")" in answer[3] and answer[3].index("(") < answer[3].index(")"):
    #     answer[3] = answer[3][answer[3].index("(")+1:answer[3].index(")")]
    # else:
    #     return await sending_messages(text="В «Куда» проблема", message=message)
    
    # Для ТК ищем значение
    if answer["тк:"] and answer["тк:"].lower() in E_CHECK_TK:
        answer["тк:"] = E_CHECK_TK[answer["тк:"].lower()]
    elif answer["тк:"]:
        for i in E_CHECK_IF_IN_STRING_TK:
            if i in answer["тк:"].lower():
                print("Сработало")
                answer["тк:"] = E_CHECK_IF_IN_STRING_TK[i]
                break

    answer = [None, None, None, answer["погрузка:"], answer["тк:"], answer["откуда:"], answer["водитель:"], answer["тягач:"], answer["договор:"], None, None, None, None, None, None, answer["ставка:"]]

    # Удаляем из ствки скобочки
    if answer[-1] and "(" in answer[-1]:
        answer[-1] = answer[-1][:answer[-1].index("(")]

    ## Если несколько договоров
    if answer[8] and answer[8].count(" + ") != 0:
        pre_answer = []
        for i in answer[8].split(" + "):
            pre_answer.append(answer[:8] + [i.strip() if "(" not in i else i[:i.index("(")].strip()] + answer[9:])
        # Создадим временный список
        answer = pre_answer
    elif answer[8]:                                                     # Один договор
        if answer[8] and "(" in answer[8]:
            answer[8] = answer[8][:answer[8].index("(")].strip()
        answer = [answer]
    else:                                                               # договор не менялся
        answer = [answer for i in range(line_amount)]

    # последняя строка с строками, чтобы добавить в сообщение
    text_to_edit = message.reply_to_message.text.split("\n")[-1]
    if line_amount > len(answer):           # Если договоров стало меньше
        # Получаем новые строки
        text_to_edit = reply_message[:reply_message.rindex("-")+1] + str(int(reply_message[reply_message.rindex("!")+1:reply_message.rindex("-")]) + len(answer) - 1)
        # Заполняем записями с "-", чтобы их вставить на место удаляемых записей
        for j in range(line_amount - len(answer)):
            answer.append([None,None] + ["-" for i in range(7)] +  [None for i in range(6)] + ["-"])

        await bt.edit_message_text(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, text=message_to_edit+"\nСтроки: "+text_to_edit)
    elif len(answer) > line_amount:         # Если добавились договоры
        # Смотрим, на какую строку можно вставить данные
        to_line = get(config["URL_FOR_TABLE_1"], reply_message[:reply_message.index("!")])
        # Вставляем данные
        put_info(answer[line_amount:], reply_message[:reply_message.index("!")], url=config["URL_FOR_TABLE_1"], start_line=to_line[0])
        try:
            await bt.edit_message_text(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, text=message_to_edit+"\n"+text_to_edit)
        except:
            pass
    else:                                     # Если договоров то же количество
        try:
            await bt.edit_message_text(chat_id=message.chat.id, message_id=message.reply_to_message.message_id, text=message_to_edit+"\n"+text_to_edit)
        except:
            pass

    # С какой строки формата A1 нужно изменять текст
    to_line = get(config["URL_FOR_TABLE_1"], reply_message[:reply_message.index("!")], line_num=line_num)
    # Если не нашли такую строку
    if len(to_line) == 1:
        return
    lines = update_info(answer[:line_amount], reply_message[:reply_message.index("!")], start_line=to_line[0], url=config["URL_FOR_TABLE_1"])
    return
