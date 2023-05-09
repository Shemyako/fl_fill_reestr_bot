# Подключаем библиотеки
import httplib2 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	
import google_module.google_config as conf

CREDENTIALS_FILE = 'google_module/token.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

# Запрос к таблице на последнюю строку в конкретном листе
def get(spreadsheetId:str, sheets:str, range_g="!A1:P10000", line_num=None, len_=1):
    """
    Ищем номер строки, в который можно вставлять данные. 
    Либо ищем в таблице столбец A (номер строки, в которой этот столбец А находится)
    spreadsheetId - url таблицы
    sheets - название листа с кавычками
    range_g - какой диапозон проверять
    line_num - значения для столбца А, которое ищем
    len_ - количество записей для вставки. Нужно для определения последнй строки
    """
    answer = []
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

    answer.append(1)
    range_ = sheets + range_g
    resp = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_).execute()

    if "values" not in resp:
        return answer
    
    line = 0
    for j in resp["values"]:
        line += 1
        if len(j) < 15:
            for i in range(16 - len(j)):
                j.append("")
        
        # Если ищем значение в столбце A
        if line_num:
            if line_num == j[0]:
                answer[-1] = line
                answer.append(f"{sheets}!{j[0]}-{int(j[0])+len_-1}")
                break
        # Если ищем просто строку, в которую можно вставить наши значения
        elif j[2] == "" and j[3] == "" and j[4] == "" and j[5] == "" and j[6] == "" and j[7] == "" and j[8] == "" and j[15] == "" and j[0] != "":
            answer[-1] = line
            answer.append(f"{sheets}!{j[0]}-{int(j[0])+len_-1}")
            break
    # if answer[0] == 1:
    #     answer[0] = len(j)
    return answer


def put_info(values, sheet, start_line=1, url = ""):
    """
    Вставка данных в таблицу
    values - Список списков, которые будем вставлять построчно
    sheet - на какой лист вставка
    start_line - на какую линию формата A1 вставлять
    url - url таблицы
    """
    # try:
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 
    body = {
        "values" : values
    }
    resp = service.spreadsheets().values().update(
        spreadsheetId=url,
        range=f"{sheet}!A{start_line}:P{start_line+len(values)-1}",
        valueInputOption="RAW",
        body=body).execute()
    return resp


def update_info(values, sheet, start_line=2, url = ""):
    """
    Обновляем значения в таблице
    values - Список списков, которые будем вставлять построчно
    sheet - на какой лист вставка
    start_line - на какую линию формата A1 вставлять
    url - url таблицы    
    """
    # try:
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 
    body = {
        "values" : values
    }
    resp = service.spreadsheets().values().update(
        spreadsheetId=url,
        range=f"{sheet}!A{start_line}:P{start_line+len(values)-1}",
        valueInputOption="RAW",
        body=body).execute()


def del_lines_g(sheet, start_line=2, line_amount=1, url=""):
    """
    Удаляем строки из таблицы
    sheet - c какого листа удаляем 
    start_line - начиная с какой линии удаляем
    line_amount - сколько строк удаляем
    url - url таблицы    
    """
    # try:
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 
    spreadsheet_data = [
        {
            "deleteDimension": {
                "range": {
                    "sheetId": sheet,
                    "dimension": "ROWS",
                    "startIndex": start_line - 1,
                    "endIndex": start_line + line_amount - 1
                }
            }

        }
    ]
    update_spreadsheet_data = {"requests": spreadsheet_data}

    # print(update_spreadsheet_data)
    resp = service.spreadsheets().batchUpdate(
        spreadsheetId=url,  
        body=update_spreadsheet_data).execute()