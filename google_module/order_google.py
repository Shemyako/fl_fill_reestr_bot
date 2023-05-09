# Подключаем библиотеки
import httplib2 
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials	
import google_module.google_config as conf
from config import config
import io

CREDENTIALS_FILE = 'google_module/token.json'  # Имя файла с закрытым ключом, вы должны подставить свое

# Читаем ключи из файла
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive'])

# Запрос к таблице на последнюю строку в конкретном листе
def get(spreadsheetId:str, sheets:str="Доверенность_тестовое", range_g="!A3"):
    """
    Смотрим номер предыдущей доверенности. Будем потом её на 1 увеличивать
    spreadsheetId - url таблицы
    sheets - название листа с кавычками
    range_g - какой диапозон проверять
    """
    answer = 1
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

    range_ = sheets + range_g
    resp = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=range_).execute()

    if "values" not in resp:
        return answer
    
    line = 0
    for j in resp["values"]:
        answer = j[0]

    return answer


def create_order(data, order_info, sheetId, url=""):
    """
    Создаём доверенность в гугл таблице
    data - словарь с начальным сообщением (погрузка, откуда, куда, водитель, ...)
    order_info - информация о доверенности [договор, [1, название товара, "","","", единицы измерения, количество]]
    sheetId - id листа из таблицы
    url - url таблицы    
    """
    contract = order_info.pop(0)
    # print(contract, order_info)
    # try:
    httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
    service = apiclient.discovery.build('sheets', 'v4', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 

    # Вставляем строки для новых товаров
    spreadsheet_data = [
        {
            "insertDimension": {
                "range": {
                "sheetId": sheetId,
                "dimension": "ROWS",
                "startIndex": 40,
                "endIndex": 40 + len(order_info) - 1
                },
                "inheritFromBefore": True
            }
        }, ]

    # Объединяем ячейки
    spreadsheet_data += [
        {
            "mergeCells": {
                "range": {
                "sheetId": sheetId,
                "startRowIndex": 39 + i,
                "endRowIndex": 39 + i+1,
                "startColumnIndex": 1,
                "endColumnIndex": 5
                },
                "mergeType": "MERGE_ALL"
            }
        } for i in range(1, len(order_info))]

    # Устанавливаем границу у ячеек
    spreadsheet_data += [
        {
            "updateBorders": {
                "range": {
                "sheetId": sheetId,
                "startRowIndex": 39 + i,
                "endRowIndex": 39 + i + 1,
                "startColumnIndex": 0,
                "endColumnIndex": 7
                },
                "top": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "blue": 0
                },
                },
                "bottom": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "blue": 0
                },
                },
                "left": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "blue": 0
                },
                },
                "right": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "blue": 0
                },
                },
                "innerVertical": {
                "style": "SOLID",
                "width": 1,
                "color": {
                    "blue": 0
                }
                } 
            }
        } for i in range(1, len(order_info))]

    update_spreadsheet_data = {"requests": spreadsheet_data}
    
    # Добавляем поля, оформляем лист
    service.spreadsheets().batchUpdate(
        spreadsheetId=url,  
        body=update_spreadsheet_data).execute()


    # Получаем номер из доверенности, чтобы его увеличить на единицу
    num = int(get(url)) + 1
    # Вносим данные
    body = {
        'valueInputOption' : 'RAW',
        'data' : [
            {   # заполняем материал
                'range' : f"{'Доверенность_тестовое'}!A40:G{40 + len(order_info) - 1}", 
                'values' : order_info
            },
            {   # Заполняем номер доверенности
                'range' : f"{'Доверенность_тестовое'}!A3", 
                'values' : [[str(num)]]
            },
            {   # заполняем дату погрузки
                'range' : f"{'Доверенность_тестовое'}!B3", 
                'values' : [[data["Погрузка:"]]]
            },
            {   # Заполняем информацию о водителе
                'range' : f"{'Доверенность_тестовое'}!D3", 
                'values' : [[data["Водитель:"]] ]
            },
            #########################################################################################
            {   # заполняем откуда
                'range' : f"{'Доверенность_тестовое'}!A6", 
                'values' : [[data["Откуда:"]]] # Разобраться с адресами
            },
            ##########################################################################################
            {   # заполняем договор
                'range' : f"{'Доверенность_тестовое'}!B13", 
                'values' : [[contract]]
            },
            {   # данные из строки "водитель" + данные из строки "тягач" (слово тягач включаем) + п/п
                'range' : f"{'Доверенность_тестовое'}!C27", 
                'values' : [[data["Водитель:"] + " Тягач: " + data["Тягач:"] + " п/п: " + data["п/п:"]]]
            },
            {   # первые 4 цифры после слов "паспорт"
                'range' : f"{'Доверенность_тестовое'}!C28", 
                'values' : [[data["Паспорт:"][:4]]] 
            },
            {   # последние 6 цифр из строки "паспорт" 
                'range' : f"{'Доверенность_тестовое'}!F28", 
                'values' : [[data["Паспорт:"][-6:]]]  
            },
            {   # данные из строки "кем выдан" и данные из строки "тел"
                'range' : f"{'Доверенность_тестовое'}!C29", 
                'values' : [[data["Кем выдан:"] + ", " + data["Тел:"]]] 
            },
            {   # из строки дата выдачи
                'range' : f"{'Доверенность_тестовое'}!C30", 
                'values' : [[data["Дата выдачи:"]]] 
            }
            ]
    }
    service.spreadsheets().values().batchUpdate(spreadsheetId=url, body=body).execute()
    
    return export_pdf(url, httpAuth, f"{config['FILE_PATH']}{data['Водитель:']}-{data['Откуда:']}.pdf")


def del_lines_g(sheet, start_line=40, line_amount=1, url=""):
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


def export_pdf(real_file_id, httpAuth, filename):
    """
    Загрузка pdf файла гугл таблицы
    real_file_id - ссылка на таблицу
    httpAuth - объект авторизации, чтобы 10 раз не авторизиароваться
    filename - как запомним файл после загрузки
    """
    # creds, _ = google.auth.default()

    try:
        
        # httpAuth = credentials.authorize(httplib2.Http()) # Авторизуемся в системе
        service = apiclient.discovery.build('drive', 'v3', http = httpAuth) # Выбираем работу с таблицами и 4 версию API 
        # create drive api client
        # service = build('drive', 'v3', credentials=creds)

        file_id = real_file_id

        # pylint: disable=maybe-no-member
        request = service.files().export_media(fileId=file_id,
                                               mimeType='application/pdf')
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # print(F'Download {int(status.progress() * 100)}.')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    
    with open(filename,"wb") as f:
        f.write(file.getvalue())

    return filename
