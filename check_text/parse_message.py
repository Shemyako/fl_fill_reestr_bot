headers = ["Имя:","Погрузка:", "Откуда:", "Куда:", "Водитель:", "Тел:", "Паспорт:", "Дата выдачи:", "Кем выдан:", "Тягач:", "п/п:", "Ставка:"]

def parse_message_text(message):
    """
    Парсим текст сообщения. На выход словарь из ключей выше. Значения - их значения из сообщения
    """
    data = {}
    text = message.reply_to_message.text.split("\n")
    for i in range(12):
        if headers[i] not in text[i]:
            # print(text[i])
            return
        data[headers[i]] = text[i][len(headers[i]):].strip()
    return data