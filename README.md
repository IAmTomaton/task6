# task6

В файле config.cnf прописываете конфигурации.

Обязательные конфигурации:
from Ваш логин на mail.ru, без @mail.ru
password ваш пароль

Файл конфигураций должен заканчиваться дополнительным пробелом.

Аргументы:
-l --last, type=int, default=0, Сколько заголовков последних писем загрузить для ознакомления

-i --index, type=int, Индекс загружаемого письма
-t --top, type=int, default=0, Сколько первых строк текста письма загрузить
-f --file, type=str, Указать какие файлы из письма нужно скачать
-o --outfile, type=str, default='', Файл в который будуть сохранятся заголовок и текст письма
-p --pathattached, type=str, default='', Дерриктория в которую будут сохранены прикреплённые файлы
-a --attached Показать список прикреплённых к письму файлов
-e --header, Загрузить заголовок письма

Файлы из видео сохранились рядом с файлом программы.
