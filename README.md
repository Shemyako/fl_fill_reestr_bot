# fl_fill_reestr_bot
Бот для создания записей в таблице реестр, а позже создания доверенностей на их основе
# Создание записи в реестре
## Ввод данных
Пользователь пишет по шаблону:

    Имя:
    Погрузка:
    Откуда:
    Куда:
    Водитель:
    Тел:
    Паспорт:
    Дата выдачи:
    Кем выдан:
    Тягач:
    п/п:
    Ставка:
    
    Договор - ТК

## Обработка
Бот проверяем введённые данные, ищет ключи для значений (откуда, куда, имя, договор, тк), отправляет это в гугл таблицу, после отправляет в общий чат сообщение

## Изменение
Сотрудник имеет возможность изменить через общий чат информацию о погрузке (информация изменится в сообщении и в гугл таблице), также может отменить погрузку (удалятся строки в гугл таблице)

### Изменение информации о погрузке
Для изменения информации о погрузке требуется в ответ на начальное сообщение ввести:

    "изменение"/"изменения"/"изменить"
    ключ, который изменяем (погрузка:/откуда:/тягач:/...) а дальше новое значение
К примеру,

    изменить
    погрузка: 10.10.2023
### Отмена погрузки
Для отмены погрузки требуется в ответ на начальное сообщение отпарвить:
"отмена погрузки"

# Создание доверенностей
Сотрудник после согласования информации о поставке должен написать в ответ на начальное сообщение:

    Договор от <название договора>
    товар количество штук единицы измерения
    
Пример:

    Доверенность от компании
    Плита термообработанная куртинское 1200/300/30 мм - 248,4 м2
    Плита термообработанная куртинское 1200/600/30 мм - 13,68 м2
Таких доверенностей может быть много в одном сообщении. Бот возьмёт информацию из сообщения, заполнит шаблон доверенности в гугл таблице, после чего скачает таблицу в pdf формате, обрежет её и вышлет pdf доверенности в общий чат с доверенностями. Далее удалит созданный pdf файл и вернёт шаблон доверенностей в нужный вид

