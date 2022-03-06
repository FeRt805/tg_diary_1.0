from prettytable import PrettyTable, ALL
from config import log

'''
Создания читабельных в телеграме таблиц с оценками, дз и тд 
'''


def tg_table(cars):
    """
    Таблица расписания ученика
    :param cars: Расписание в виде словаря
    :return: Расписание в таблице prettytable
    """
    # cars = {'Понедельник': ['Литературное чтение (10:30 - 11:15)', 'Иностранный язык (9:30 - 10:15)', 'Математика (
    # 11:30 - 12:15)', 'Окружающий мир (8:30 - 9:15)', 'Технология (12:30 - 13:15)'], 'Вторник': ['Физическая
    # культура (10:30 - 11:15)', 'Русский язык (11:30 - 12:15)', 'Русский язык (9:30 - 10:15)', 'Математика (12:30 -
    # 13:15)', 'Музыка (8:30 - 9:15)'], 'Среда': ['Музыка (8:30 - 9:15)', 'Музыка (10:30 - 11:15)', 'Музыка (11:30 -
    # 12:15)', 'Иностранный язык (9:30 - 10:15)'], 'Четверг': ['Окружающий мир (10:30 - 11:15)', 'Математика (8:30 -
    # 9:15)', 'Математика (11:30 - 12:15)', 'Окружающий мир (12:30 - 13:15)', 'Изобразительное искусство (9:30 -
    # 10:15)'], 'Пятница': ['Технология (9:30 - 10:15)', 'Литературное чтение (8:30 - 9:15)', 'Русский язык (11:30 -
    # 12:15)', 'Музыка (12:30 - 13:15)', 'Технология (10:30 - 11:15)'], 'Суббота': []}

    out = "\n"
    for x in cars:
        table = PrettyTable()
        table.max_table_width = 34
        table.min_table_width = 34
        table.border = True
        table.field_names = [x]
        for y in cars[x]:
            table.add_row([y])

        out += str(table)
        out += "\n"

    return out


def deals_list(data):
    if len(data) == 0:
        return "\nУ вас пока нет никаких задач\n_Но вы можете добавить их, нажав на кнопку \n\"Добавить задание\"_"
    out = "\n"
    for i in data:
        out += str(i) + "." + data[i] + "\n"
    return out


def marks_table(data, current_lesson):
    out = "\n"
    if isinstance(data, dict):
        for lesson in data:
            for i in range(len(data[lesson]) - 1):
                for j in range(len(data[lesson]) - i - 1):
                    if data[lesson][j][1] > data[lesson][j + 1][1]:
                        data[lesson][j], data[lesson][j + 1] = data[lesson][j + 1], data[lesson][j]
        for lesson in data:
            table = PrettyTable()
            table.max_table_width = 34
            table.min_table_width = 34
            table.hrules = ALL
            table.border = True
            table.padding_width = 1
            table.title = lesson
            table._max_width = {"Дата": 6, "Оценка": 28}
            table.field_names = ["Дата", "Оценка"]
            all_data = []
            all_marks = []
            for mark, day in data[lesson]:
                day = day.strftime('%d/%m/%Y')
                mark = str(mark) + " "
                if len(all_data) != 0 and day == all_data[-1]:
                    all_marks[-1] += mark
                else:
                    all_data.append(day)
                    all_marks.append(mark)
            for i in range(len(all_data)):
                table.add_row([all_data[i], all_marks[i]])
            out += str(table) + "\n\n"
    else:
        lesson = current_lesson
        table = PrettyTable()
        table.max_table_width = 34
        table.min_table_width = 34
        table.hrules = ALL
        table.border = True
        table.padding_width = 1
        table.title = lesson
        table._max_width = {"Дата": 6, "Оценка": 28}
        table.field_names = ["Дата", "Оценка"]

        all_data = []
        all_marks = []
        for mark, day in data:
            day = day.strftime('%d/%m/%Y')
            mark = str(mark) + " "
            if len(all_data) != 0 and day == all_data[-1]:
                all_marks[-1] += mark
            else:
                all_data.append(day)
                all_marks.append(mark)
        for i in range(len(all_data)):
            table.add_row([all_data[i], all_marks[i]])
        out += str(table) + "\n"
    return out


# print(marks_table({'Русский язык': [[5, datetime.datetime(2022, 1, 13, 0, 0)], [4, datetime.datetime(2022, 1, 12,
# 0, 0)], [2, datetime.datetime(2022, 1, 15, 0, 0)]], 'Литературное чтение': [], 'Иностранный язык': [],
# 'Математика': [], 'Окружающий мир': [], 'Изобразительное искусство': [[5, datetime.datetime(2022, 1, 9, 0, 0)]],
# 'Музыка': [], 'Технология': [], 'Физическая культура': []}, "Все оценки"))

# print(marks_table({'Русский язык': [[5, datetime.datetime(2022, 1, 13, 0, 0)], [4, datetime.datetime(2022, 1, 13,
# 0, 0)]], 'Литературное чтение': [[4, datetime.datetime(2022, 1, 9, 0, 0)], [4, datetime.datetime(2022, 1, 9, 0,
# 0)]], 'Иностранный язык': [[4, datetime.datetime(2022, 1, 13, 0, 0)]], 'Математика': [], 'Окружающий мир': [],
# 'Изобразительное искусство': [[4, datetime.datetime(2022, 1, 11, 0, 0)], [4, datetime.datetime(2022, 1, 12, 0,
# 0)]], 'Музыка': [[4, datetime.datetime(2022, 1, 10, 0, 0)], [4, datetime.datetime(2022, 1, 10, 0, 0)], [5,
# datetime.datetime(2022, 1, 12, 0, 0)]], 'Технология': [[4, datetime.datetime(2022, 1, 11, 0, 0)]], 'Физическая
# культура': [[4, datetime.datetime(2022, 1, 10, 0, 0)]]} ))


def hometask_table(data, current_lesson):
    tick = "✓"  # "√" #"⇑" # "✔" # "☑" # "✓"
    cross = "✘"  # "x" #"⇓"# "✘" # "☒" # "☓" # "✘"
    out = "\n"
    if isinstance(data, dict):
        for lesson in data:
            for i in range(len(data[lesson]) - 1):
                for j in range(len(data[lesson]) - i - 1):
                    if data[lesson][j][1] > data[lesson][j + 1][1]:
                        data[lesson][j], data[lesson][j + 1] = data[lesson][j + 1], data[lesson][j]
        for lesson in data:
            table = PrettyTable()
            table.max_table_width = 34
            table.hrules = ALL
            table.border = True
            table.padding_width = 1
            table.title = lesson
            table._max_width = {"Дата": 6, "Д/З": 14, f"{tick}/{cross}": 1}
            table.field_names = ["Дата", "Д/З", f"{tick}/{cross}"]

            all_data = []
            all_marks = []
            all_done = []
            for task, day, done in data[lesson]:
                day = day.strftime('%d/%m/%Y')
                task = str(task) + " "
                if len(all_data) != 0 and day == all_data[-1]:
                    all_marks[-1] += task
                else:
                    all_data.append(day)
                    all_marks.append(task)
                    all_done.append(done)
            for i in range(len(all_data)):
                d = all_done[i]
                if d is True:
                    d = tick
                else:
                    d = cross
                table.add_row([all_data[i], all_marks[i], d])
            out += str(table) + "\n\n"
    else:
        lesson = current_lesson
        table = PrettyTable()
        table.max_table_width = 34

        table.hrules = ALL
        table.border = True
        table.padding_width = 1
        table.title = lesson
        table._max_width = {"Дата": 6, "Д/З": 14, f"{tick}/{cross}": 1}
        table.field_names = ["Дата", "Д/З", f"{tick}/{cross}"]

        all_data = []
        all_marks = []
        all_done = []
        for task, day, done in data:
            day = day.strftime('%d/%m/%Y')
            task = str(task) + " "
            if len(all_data) != 0 and day == all_data[-1]:
                all_marks[-1] += task
            else:
                all_data.append(day)
                all_marks.append(task)
                all_done.append(done)
        for i in range(len(all_data)):
            d = all_done[i]
            if d is True:
                d = tick
            else:
                d = cross

            table.add_row([all_data[i], all_marks[i], d])
        out += str(table) + "\n"
    return out

# print(hometask_table({'Русский язык': [['Учебник §58-62 пересказ', datetime.datetime(2022, 1, 16, 0, 0), False],
# ['Учебник §71-72 пересказ', datetime.datetime(2022, 1, 18, 0, 0), False]], 'Литературное чтение': [['Учебник стр.
# 98 внимательно читать', datetime.datetime(2022, 1, 18, 0, 0), False], ['Учебник упр. 15', datetime.datetime(2022,
# 1, 18, 0, 0), False]], 'Иностранный язык': [], 'Математика': [], 'Окружающий мир': [['Учебник стр. 53-56 читать',
# datetime.datetime(2022, 1, 17, 0, 0), False]], 'Изобразительное искусство': [], 'Музыка': [], 'Технология': [],
# 'Физическая культура': [['Пресс качат, бегит, турник и анжуманя', datetime.datetime(2022, 1, 17, 0, 0), False],
# ['Пресс качат, бегит, турник и анжуманя', datetime.datetime(2022, 1, 18, 0, 0), False]]}, "Все задания"))
#
#
# # Вывод программы
# if log:
#     print("Успешное создание таблицы")
#     print("#########################")
#
