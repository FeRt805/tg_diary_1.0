import russian_names
import nickname_generator
import random
import datetime
from dateutil import parser as dtparser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from making_db_structure import Schools, Subjects, Classes, Students, Studying, Hometasks, Marks, Timetables, Base
from tg_table import tg_table
# from config import log, admin, sasha1, schools_num_min, schools_num_max, classes_to_remove_min,
# classes_to_remove_max, students_in_class_min, students_in_class_max, marks_chance_min, marks_chance_max,
# marks_chance_edge
from config import *
'''
Генератор школ, классов, учеников, дз, отметок и тд
'''

############################################ Генерация данных ##########################################################

TODAY = datetime.date(1, 1, 1).today()
study_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


def get_random_marks():
    """
    :return: Random mark 2-5
    """
    x = random.randint(0, 100)

    two = 5  # 5%
    three = 15  # 10%
    four = 75  # 60%
    five = 100  # 25%
    if x in range(0, two + 1):
        return 2
    elif x in range(two, three + 1):
        return 3
    elif x in range(three, four + 1):
        return 4
    elif x in range(four, five + 1):
        return 5


def get_hometask_text():
    """
    :return: Random hometask
    """
    x = random.randint(10, 100)
    hometask_text = [f"Учебник стр. {random.randint(10, 100)} внимательно читать",
                     f"Рабочая тетрадь стр. {random.randint(10, 100)}",
                     f"Учебник стр. {x}-{x + random.randint(1, 5)} читать",
                     f"Упражнение №{random.randint(50, 150)}",
                     f"Рабочая тетрадь стр. {x}-{x + random.randint(1, 5)} сделать",
                     f"Учебник упр. {random.randint(10, 100)}",
                     f"Рабочая тетрадь упр. {x}-{x + random.randint(1, 5)}",
                     f"Учебник §{random.randint(10, 30)}",
                     f"Учебник §{x}-{x + random.randint(1, 5)} пересказ",
                     "Готовимся к контрольной по всем темам"
                     ]
    return random.choice(hometask_text)


def get_hometasks(lessons_source):
    lessons = lessons_source.copy()
    hometasks_today = {}
    random.shuffle(lessons)
    task_num = random.randint(3, len(lessons) - 1)  # Количество заданий
    for i in range(task_num):
        if lessons[i][:lessons[i].find("(")].startswith("Доп."):
            continue
        if lessons[i][:lessons[i].find("(")] != "Физическая культура ":
            hometasks_today.update({str(lessons[i]): get_hometask_text()})
        else:
            pe_hw = ["Пресс качат, бегит, турник и анжуманя",
                     "1) бегит 2) анжуманя 3) пресс качат 4) ищем разработчика со знанием React Native уровня "
                     "джун+/миддл в международную команду занимающуюся разработкой и продвижением мобильных "
                     "приложений, у нас несколько продуктов, зп в евро!!"]

            if random.randint(0, 100) > 10:
                hometasks_today.update({str(lessons[i]): pe_hw[0]})
            else:
                hometasks_today.update({str(lessons[i]): pe_hw[1]})

    return hometasks_today


def get_lesson_time(class_current):
    """
    :param class_current: Current lesson in order
    :return: Lesson time
    """
    lessons_time = ["8:30 - 9:15", "9:30 - 10:15", "10:30 - 11:15", "11:30 - 12:15", "12:30 - 13:15",
                    "13:30 - 14:15", "14:30 - 15:15", "15:30 - 16:15", "16:30 - 17:15", "17:30 - 18:15"]
    return "(" + lessons_time[class_current] + ")"


def translit(word):
    dictionary = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i',
                  'й': 'i',
                  'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                  'ф': 'f',
                  'х': 'h', 'ц': 'c', 'ч': 'cz', 'ш': 'sh', 'щ': 'scz', 'ъ': '', 'ы': 'y', 'ь': 'b', 'э': 'e', 'ю': 'u',
                  'я': 'ja',
                  'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'E', 'Ж': 'ZH', 'З': 'Z', 'И': 'I',
                  'Й': 'I',
                  'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                  'Ф': 'F',
                  'Х': 'H', 'Ц': 'C', 'Ч': 'CZ', 'Ш': 'SH', 'Щ': 'SCH', 'Ъ': '', 'Ы': 'y', 'Ь': 'b', 'Э': 'E', 'Ю': 'U',
                  'Я': 'YA',
                  ',': ',', '?': '?', ' ': '_', '~': '~', '!': '!', '@': '@', '#': '#', '$': '$', '%': '%', '^': '^',
                  '&': '&',
                  '*': '*', '(': '(', ')': ')', '-': '-', '=': '=', '+': '+', ':': ':', ';': ';', '<': '<', '>': '>',
                  "'": "'",
                  '"': '"', '\\': '\\', '/': '/', '№': '#', '[': '[', ']': ']', '{': '{', '}': '}', 'ґ': 'r', 'ї': 'r',
                  'є': 'e',
                  'Ґ': 'g', 'Ї': 'i', 'Є': 'e', '—': '-'}

    new_word = ""
    for i in word:
        if i in dictionary.keys():
            new_word += dictionary[i]
        else:
            new_word += i

    return new_word


def add_symbol_at_50_chance(x):
    if bool(random.randint(0, 1)):
        return x
    else:
        return ""


def get_nickname(name=""):
    """
    :return: Returns a nickname
    """
    if random.randint(0, 10) > 4 or name == "":
        # Use random nickname generator
        nickname_generator.MIN_LENGTH = 4
        nickname_generator.MAX_LENGTH = 10

        n = nickname_generator.generate()

    else:
        # Translit nickname
        n = translit(name)

    # Randomly add nums
    r = random.randint(1, 100)
    if r > 60:
        n = n + add_symbol_at_50_chance("_") + str(random.randint(1, 1000))

    n = n.lower()
    return n


# Парсинг реальных школ Москвы

# from bs4 import BeautifulSoup
# import requests
# # Schools
# url = "https://ru.wikipedia.org/wiki/Список_школ_Москвы"
# r = requests.get(url)
# soup = BeautifulSoup(r.text)
# t = soup.find_all("ol")
# s = []
# for i in t:
#     i = str(i)
#     s.append(i.split("<li>"))
#
# print(s)

def generate():
    global schools, subjects, classes, students, studying, hometasks, marks, timetables
    # schools_num = random.randint(7, 15)  # Количество школ
    schools_num = random.randint(schools_num_min, schools_num_max)  # Количество школ
    schools = []
    school_prenames = ["ГБОУ Школа №", "Лицей №", "Закрытая Школа №"]
    for i in range(1, schools_num + 1):
        while 1:  # make unique
            school_name = random.choice(school_prenames) + str(random.randint(1, 1000))
            if not [school_name] in schools:
                schools.append([school_name])
                break
    if log:
        print("Успешная генерация Школ")
        print("#######################")
    ####################################################################################################################

    class_letters = ["А", "Б", "В"]

    classes = []  # Classes table
    for school_id in range(1, len(schools) + 1):
        classes_school = []  # Классы в одной школе
        # Все возможные классы
        for year in range(1, 12):
            for letter in class_letters:
                classes_school.append(f"{year}{letter}")

        # Удаляем случайные классы
        classes_to_remove = random.randint(classes_to_remove_min, classes_to_remove_max)  # Количество удаляемых классов
        # classes_to_remove = random.randint(0, 8)  # Количество удаляемых классов
        # classes_to_remove = random.randint(25, 30)  # Количество удаляемых классов
        for i in range(classes_to_remove):
            classes_school.remove(random.choice(classes_school))

        # Добавляем в общий список
        for cl in classes_school:
            classes.append([cl, school_id])

    if log:
        print("Успешная генерация Классов")
        print("##########################")
    ####################################################################################################################

    RN = russian_names.RussianNames(patronymic=False)

    students = []  # Students table
    all_nicks = []
    for class_id in range(1, len(classes)):
        # students_in_class = random.randint(20, 35)  # Количество человек в классе
        # students_in_class = random.randint(2, 5)  # Количество человек в классе
        students_in_class = random.randint(students_in_class_min, students_in_class_max)  # Количество человек в классе
        for i in range(students_in_class):
            name = RN.get_person()
            while 1:  # make unique
                nick = get_nickname(name)
                if not nick in all_nicks:
                    all_nicks.append(nick)
                    break
            # password = "tg_diary"

            # Уникальный пароль
            password = "tg_diary_" + str(class_id) + "_" + translit(classes[class_id][0]) + "_" + translit(
                name.split()[1])

            info = f"Привет, я {name}!"
            students.append([nick, password, class_id, info, "", ""])
    if log:
        print("Успешная генерация Учеников")
        print("###########################")
    ####################################################################################################################

    subjects_1_4 = ['Русский язык', 'Литературное чтение', 'Иностранный язык', 'Математика', 'Окружающий мир',
                    'ИЗО', 'Музыка', 'Технология', 'Физическая культура']

    subjects_5_6 = ['Русский язык', 'Литература', 'Иностранный язык', 'Математика', "География", "Информатика",
                    'Музыка', 'Физ-ра', "История", "Биология"]

    subjects_7_9 = ['Русский язык', 'Литература', 'Иностранный язык', 'Алгебра', "Геометрия", "География", "Физика",
                    "ОБЖ", 'Химия', "Информатика",
                    'Физ-ра', "История", "Биология"]

    subjects_10_11 = ['Русский язык', 'Литература', 'Иностранный язык', 'Алгебра', "Геометрия", "География", "Физика",
                      "ОБЖ", 'Химия', 'Технология', "Естествознание", "Информатика",
                      'Физическая культура', "История", "Биология", "Экология"]

    subjects_extra = ["Экология", "Информатика", 'Русский язык', 'Иностранный язык', "Математика", "Физика"]

    subjects = [*subjects_1_4, *subjects_5_6, *subjects_7_9, *subjects_10_11]

    subjects = list(set(subjects))

    if log:
        print("Успешная генерация Предметов")
        print("############################")

    ####################################################################################################################
    studying = []  # Studying table
    for student_id, student in enumerate(students):
        class_current = classes[student[2] - 1][0]
        class_num = int(class_current[:-1])  # Класс в котором учиться человек
        # Проверка на класс обучения
        student_id += 1
        if 5 > class_num:
            for subject in subjects_1_4:
                subject_id = subjects.index(subject) + 1
                studying.append([student_id, subject_id])
        elif 7 > class_num >= 5:
            for subject in subjects_5_6:
                subject_id = subjects.index(subject) + 1
                studying.append([student_id, subject_id])
        elif 10 > class_num >= 7:
            for subject in subjects_7_9:
                subject_id = subjects.index(subject) + 1
                studying.append([student_id, subject_id])
        elif class_num >= 10:
            for subject in subjects_10_11:
                subject_id = subjects.index(subject) + 1
                studying.append([student_id, subject_id])
    if log:
        print("Успешная генерация Таблицы обучения")
        print("###################################")

    ####################################################################################################################

    timetables_class = []
    timetables = []  # Timetables table
    for class_id, class_current in enumerate(classes):
        class_num = int(class_current[0][:-1])
        class_id += 1
        timetable = {"Понедельник": [], "Вторник": [], "Среда": [], "Четверг": [], "Пятница": [], "Суббота": []}
        if 5 > class_num:
            for key in timetable.keys():
                if key != "Суббота":
                    k = random.randint(4, 5)  # Количество уроков в день
                    for i in range(k):
                        q = random.choice(subjects_1_4)  # Меньше шанс повторяющихся предметов
                        if q in timetable[key]:
                            timetable[key].append(random.choice(subjects_1_4) + " " + get_lesson_time(i))
                        else:
                            timetable[key].append(random.choice(subjects_1_4) + " " + get_lesson_time(i))

        elif 7 > class_num >= 5:
            for key in timetable.keys():
                if key != "Суббота":
                    k = random.randint(5, 6)  # Количество уроков в день
                    for i in range(k):
                        q = random.choice(subjects_5_6)  # Меньше шанс повторяющихся предметов
                        if q in timetable[key]:
                            timetable[key].append(random.choice(subjects_5_6) + " " + get_lesson_time(i))
                        else:
                            timetable[key].append(random.choice(subjects_5_6) + " " + get_lesson_time(i))
        elif 10 > class_num >= 7:
            for key in timetable.keys():
                if key != "Суббота":
                    k = random.randint(5, 7)  # Количество уроков в день
                    for i in range(k):
                        q = random.choice(subjects_7_9)  # Меньше шанс повторяющихся предметов
                        if q in timetable[key]:
                            timetable[key].append(random.choice(subjects_7_9) + " " + get_lesson_time(i))
                        else:
                            timetable[key].append(random.choice(subjects_7_9) + " " + get_lesson_time(i))

        elif class_num >= 10:
            for key in timetable.keys():
                if key != "Суббота":
                    k = random.randint(6, 8)  # Количество уроков в день
                    for i in range(k):
                        q = random.choice(subjects_10_11)  # Меньше шанс повторяющихся предметов
                        if q in timetable[key]:
                            timetable[key].append(random.choice(subjects_10_11) + " " + get_lesson_time(i))
                        else:
                            timetable[key].append(random.choice(subjects_10_11) + " " + get_lesson_time(i))
        timetables_class.append(timetable)

    # Заполнения расписания для каждого ученика
    for student_id, student in enumerate(students):
        student_id += 1
        # timetable = timetables_class[student[2]-1]  # Расписание класса ученика
        class_id = student[2] - 1
        timetable = timetables_class[class_id]

        # class_current = classes[student[2]]
        # class_num = int(class_current[0][:-1])
        # print(class_num, timetable)

        # Если старше 4 класса, тогда допы с 30% вероятности
        if int(classes[student[2]][0][0]) > 4:
            if random.randint(0, 100) > 70:
                timetable[random.choice(study_days)].append(
                    "Доп. " + random.choice(subjects_extra) + " " + get_lesson_time(random.randint(8, 9))
                )

        timetables.append([student_id, timetable])
    if log:
        print("Успешная генерация Расписаний")
        print("#############################")
    ####################################################################################################################
    # print(timetables[-1])
    hometasks = []  # Hometasks table
    ddays = []  # Дни для домашних заданий, дни будущих уроков
    d = TODAY

    # Дни до конца недели
    for i, day in enumerate(days):
        if i > TODAY.weekday():
            # d = datetime.date(d.year, d.month, d.day + 1)
            date_obj = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
            date_obj += datetime.timedelta(days=1)
            d = datetime.date(date_obj.year, date_obj.month, date_obj.day)
            ddays.append(day + " " + str(d))

    # Дни следующей недели
    d_o = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
    d_o += datetime.timedelta(days=6 - TODAY.weekday())
    for i in range(7):
        d_o += datetime.timedelta(days=1)
        d = datetime.date(d_o.year, d_o.month, d_o.day)

        ddays.append(days[i] + " " + str(d))

    # Генерим домашние задания
    for timetables_id, timetable_list in enumerate(timetables):
        student_id = timetable_list[0]
        timetable = timetable_list[1]
        timetables_id += 1
        for day in ddays:
            day_real = day[:day.find(" ")]
            if day_real != "Воскресенье" and len(timetable[day_real]) > 3:
                if day_real == "Суббота" and random.randint(0, 100) > 10:
                    # Если суббота то шанс дз меньше
                    continue
                else:
                    tasks = get_hometasks(timetable[day_real])
                    for key in tasks.keys():
                        day_list_dates = list(map(lambda x: int(x), day[day.find(" "):].split("-")))
                        day_date = datetime.date(*day_list_dates)  # Дата дз
                        hometasks.append([timetables_id, key, tasks[key], day_date, False])
    if log:
        print("Успешная генерация ДЗ")
        print("#####################")
    ####################################################################################################################
    this_and_previous_week_days = []

    # Дни предыдущей недели
    d_o = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
    d_o += datetime.timedelta(days=-8 - TODAY.weekday())
    for i in range(7):
        d_o += datetime.timedelta(days=1)
        d = datetime.date(d_o.year, d_o.month, d_o.day)

        this_and_previous_week_days.append(days[i] + " " + str(d))

    # Дни до конца этой недели
    d_o = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
    d_o += datetime.timedelta(days=-TODAY.weekday() - 1)
    for i, day in enumerate(days):
        if i < TODAY.weekday():
            d_o += datetime.timedelta(days=1)
            d = datetime.date(d_o.year, d_o.month, d_o.day)
            this_and_previous_week_days.append(day + " " + str(d))

    # print(this_and_previous_week_days)
    # ['Понедельник 2022-02-14', 'Вторник 2022-02-15', 'Среда 2022-02-16',
    # 'Четверг 2022-02-17', 'Пятница 2022-02-18', 'Суббота 2022-02-19', 'Воскресенье 2022-02-20', 'Понедельник
    # 2022-02-21', 'Вторник 2022-02-22', 'Среда 2022-02-23', 'Четверг 2022-02-24', 'Пятница 2022-02-25']
    marks = []  # Marks table

    for timetables_id, timetable_list in enumerate(timetables):
        student_id = timetable_list[0]
        timetable = timetable_list[1]
        timetables_id += 1
        for day in this_and_previous_week_days:
            day_real = day[:day.find(" ")]
            if day_real != "Воскресенье" and day_real != "Суббота" and len(timetable[day_real]) > 3:
                # subject_to_mark = random.choice(timetable[day_real])  # Предмет на который ставиться оценка
                for subject_to_mark in timetable[day_real]:
                    if random.randint(marks_chance_min, marks_chance_max) > marks_chance_edge:
                        # Шанс 65% на оценку по каждому предмету
                        if subject_to_mark.startswith("Доп."):
                            continue
                        day_list_dates = list(map(lambda x: int(x), day[day.find(" "):].split("-")))
                        day_date = datetime.date(*day_list_dates)  # Дата оценки
                        marks.append([timetables_id, subject_to_mark, student_id, get_random_marks(), day_date])


    if log:
        print("Успешная генерация Оценок")
        print("#########################")


def load():
    ########################################### Загрузка в базу данных #################################################

    # Session

    engine = create_engine('sqlite:///data.db')

    Base.metadata.drop_all(engine)  # Удаление всех таблиц
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)  # Как только у вас появится engine
    session = Session()

    for school in schools:
        session.add(Schools(*school))

    for subject in subjects:
        session.add(Subjects(subject))

    for class_ in classes:
        session.add(Classes(*class_))

    for student in students:
        session.add(Students(*student))

    # My profile
    sasha = session.query(Students).filter_by(id=1).first()  # на место донора под id 1
    sasha.nickname = sasha1[0]
    sasha.password = sasha1[1]
    sasha.tg_id = sasha1[2]
    # test profile
    teacher = session.query(Students).filter_by(id=2).first()
    teacher.nickname = "test"
    teacher.password = "123"
    # admin profile
    adm = session.query(Students).filter_by(id=3).first()
    adm.nickname = admin[0]
    adm.password = admin[1]

    for st in studying:
        session.add(Studying(*st))

    for task in hometasks:
        session.add(Hometasks(*task))

    for mark in marks:
        session.add(Marks(*mark))

    for timetable in timetables:
        student_id = timetable[0]
        tt = timetable[1]
        table = tg_table(tt)
        session.add(Timetables(student_id, table, tt))

    session.commit()


if __name__ == '__main__':
    # next_day()
    generate()
    # Вывод программы
    if log:
        print("Успешная генерация данных")
        print("#########################")

    load()
    # Вывод программы
    if log:
        print("Успешная загрузка данных")
        print("#########################")
