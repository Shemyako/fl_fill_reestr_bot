from aiogram import Router, Bot, types
from google_module.google_module import put_info, update_info, get, del_lines_g
from google_module.google_config import F_IN_STRING, F_CHECK_IF_IN_STRING, NAME_CHECK, E_CHECK_TK, E_CHECK_IF_IN_STRING_TK, SHEETS_ID
from check_text.sending_message import sending_messages
from order_module.order_config import MEASUREMENTS, IF_IN_CONTRACTS, CONTRACTS, IF_IN_WHERE_IS_FROM, WHERE_IS_FROM
from order_module.work_with_pdf import split_file
from google_module.order_google import create_order, del_lines_g
from datetime import date
import json, os

# Чтение конфига
from config import config

# Заголовки начального сообщения
headers = ["Имя:","Погрузка:", "Откуда:", "Куда:", "Водитель:", "Тел:", "Паспорт:", "Дата выдачи:", "Кем выдан:", "Тягач:", "п/п:", "Ставка:"]


def define_contract(contract):
    """
    Определяем какой именно у нас контракт
    """
    # Проходимся, прибавляя букву и смотрим, есть ли такое в контрактах
    for i in range(1,len(contract)+1):
        if contract[:i].lower() in CONTRACTS:
            return CONTRACTS[contract[:i].lower()]
        
    for i in IF_IN_CONTRACTS:
        if i in contract.lower():
            return IF_IN_CONTRACTS[i]
        
    return contract


async def get_order(message, bt):
    """
    !Из reply_message получаем информацию для вноса в таблицу
    Загружаем информацию в таблицу
    Выгружаем таблицу
    Обрезаем таблицу
    Высылаем таблицу
    """
    data = {}
    text = message.reply_to_message.text.split("\n")

    # Считываем все заголовки
    for i in range(12):
        if headers[i] not in text[i]:
            # print(text[i])
            return
        data[headers[i]] = text[i][len(headers[i]):].strip()

    # Убираем из паспорта пробелы
    data["Паспорт:"] = data["Паспорт:"].replace(" ", "")
    # Откуда обрабатываем
    data["Откуда:"] = data["Откуда:"].split(" + ") 
    from_ = []
    for i in data["Откуда:"]:
        if "(" in i and ")" in i and i.index("(") < i.index(")"):
            if i.lower() == "датсун":
                continue
            i = i[i.index("(")+1:i.index(")")].strip()

            # Смотрим, есть ли в словарях такое ОТКУДА
            if i.lower() in WHERE_IS_FROM:
                i = WHERE_IS_FROM[i.lower()]
            else:
                for j in IF_IN_WHERE_IS_FROM:
                    if j in i.lower():
                        i = IF_IN_WHERE_IS_FROM[j]
                        break

        from_.append(i)
    data["Откуда:"] = from_[:]
    del from_

    # Обрабатываем погрузку
    if "/" in data["Погрузка:"]:        # Если есть / в дате, выберем всё, что правее
        data["Погрузка:"] = data["Погрузка:"][data["Погрузка:"].rindex("/")+1:].strip() 
    if len(data["Погрузка:"]) < 6:      # Если нет года, добавим его
        data["Погрузка:"] += f".{date.today().year}"

    # Получаем договоры
    data["Договоры:"] = text[13][:text[13].index(" - ")].split(" + ")

    order_info = []
    order_message_text = message.text.split("\n")
    for i in order_message_text:
        # Если новая доверенность
        if i.lower().strip()[:3] == "от ":
            order_info.append([define_contract(i.strip()[3:].strip())])
            continue
        elif i.lower().strip()[:15] == "доверенность от":
            order_info.append([define_contract(i.strip()[15:].strip())])
            continue
        order_info[-1].append(i.strip())

    # Проходимся по каждой доверенности
    worker_orders = []
    for order in order_info:
        counter = 0
        worker_orders.append([order[0]])
        for i in order[1:]:             # По каждому товару из доверенности
            counter += 1
            # Обрезаем символ в начале строки, если есть ("1"/"-"/"1.")
            if i.index(" ") < 4 and (i[0] == "-" or i[0] in "0123456789"):
                i = i[i.index(" ")+1:]

            # Ищем в окончании "количество" или "-"
            if "количество" in i:
                name = i[:i.lower().rindex("количество")].strip()
                amount = i[i.lower().rindex("количество")+10:].strip()
            else:
                name = i[:i.rindex("-")].strip()
                amount = i[i.rindex("-")+1:].strip()

            # Ищем размерность и количество
            measurement = ""
            for j in range(len(amount)):
                if amount[j] not in "0123456789":
                    measurement = amount[j:].strip()
                    amount = amount[:j]
                    break

            if measurement.lower() in MEASUREMENTS:
                measurement = MEASUREMENTS[measurement.lower()]

            # добавляем в список текущей доверенности список текущего товара (имя, количество, размерность)
            worker_orders[-1].append([str(counter), name,"","","",measurement,amount])

    del order_info
    

    for order in worker_orders:
        for from_ in data["Откуда:"]:
            data_ = data.copy()
            data_["Откуда:"] = from_
            print(order, data_)
            # Изменяем договор и зугружаем его
            filename = create_order(data_, order[:], sheetId=config["ORDER_SHEET_ID"], url=config["URL_FOR_ORDER_TABLE"])
            # Разрезаем его
            split_file(filename, filename)
            # Отправляем в чат
            await sending_messages(id=config["CHAT_FOR_ORDER"], bt=bt, filename=filename)
            # Удаляем файл
            os.remove(filename)
            # Удаляем строки ненужные из доверенности (если товара больше одного)
            if (len(order) - 2) != 0:
                del_lines_g(config["ORDER_SHEET_ID"], line_amount=len(order) - 2, url=config["URL_FOR_ORDER_TABLE"])


