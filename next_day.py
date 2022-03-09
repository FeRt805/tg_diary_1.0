import datetime
from dateutil import parser as dtparser
from get_from_db import get_timetables_all
import random
from filling_db import get_hometasks, get_random_marks, days
from config import log
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from making_db_structure import Schools, Subjects, Classes, Students, Studying, Hometasks, Marks, Timetables, Base

tts = get_timetables_all()


# Не надо, пожалуйста, спамить)))
def next_day(days_passed=1):
    TODAY = datetime.date(1, 1, 1).today()
    # next day
    d_o = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
    d_o += datetime.timedelta(days=days_passed)
    TODAY = datetime.date(d_o.year, d_o.month, d_o.day)

    hometasks = []  # Hometasks table
    ddays = []  # Дни для домашних заданий, дни будущих уроков

    # Дни до конца недели
    for i, day in enumerate(days):
        if i > TODAY.weekday():
            # d = datetime.date(d.year, d.month, d.day + 1)
            date_obj = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
            date_obj += datetime.timedelta(days=1)
            d = datetime.date(date_obj.year, date_obj.month, date_obj.day)
            ddays.append(day + " " + str(d))

    # Дни следующей половины недели
    d_o = dtparser.parse(TODAY.strftime('%Y-%m-%d'))
    d_o += datetime.timedelta(days=6 - TODAY.weekday())
    for i in range(3):
        d_o += datetime.timedelta(days=1)
        d = datetime.date(d_o.year, d_o.month, d_o.day)
        ddays.append(days[i] + " " + str(d))

    # # меньше заданий
    # random.shuffle(ddays)
    # ddays = ddays[random.randint(0, 3):random.randint(len(days)-3, len(ddays))]
    # Генерим домашние задания
    for timetables_id, timetable in enumerate(tts):
        timetables_id += 1
        day_real = days[TODAY.weekday()]

        for day in ddays:
            if day_real != "Воскресенье" and len(timetable[day_real]) > 3:
                if day_real == "Суббота" and random.randint(0, 100) > 10:
                    # Если суббота то шанс дз меньше
                    continue
                else:
                    tasks = get_hometasks(timetable[day_real])
                    for key in tasks.keys():
                        if key in timetable[day_real]:
                            day_list_dates = list(map(lambda x: int(x), day[day.find(" "):].split("-")))
                            day_date = datetime.date(*day_list_dates)  # Дата дз
                            hometasks.append([timetables_id, key, tasks[key], day_date, False])

    ####################################################################################################################

    this_and_previous_week_days = [days[TODAY.weekday()] + " " + str(TODAY)]

    marks = []  # Marks table

    for timetables_id, timetable in enumerate(tts):
        timetables_id += 1
        student_id = timetables_id

        for day in this_and_previous_week_days:
            day_real = day[:day.find(" ")]
            if day_real != "Воскресенье" and day_real != "Суббота" and len(timetable[day_real]) > 3:
                # subject_to_mark = random.choice(timetable[day_real])  # Предмет на который ставиться оценка
                for subject_to_mark in timetable[day_real]:
                    if random.randint(0, 100) > 35:  # Шанс 65% на оценку по каждому предмету
                        if subject_to_mark.startswith("Доп."):
                            continue
                        day_list_dates = list(map(lambda x: int(x), day[day.find(" "):].split("-")))
                        day_date = datetime.date(*day_list_dates)  # Дата оценки
                        marks.append([timetables_id, subject_to_mark, student_id, get_random_marks(), day_date])

    ########################################### Загрузка в базу данных #################################################
    # print(hometasks)
    # print(marks)

    engine = create_engine('sqlite:///data.db')

    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)  # Как только у вас появится engine
    session = Session()

    for task in hometasks:
        session.add(Hometasks(*task))

    if log:
        print("Успешное обновление ДЗ")
        print("######################")

    for mark in marks:
        session.add(Marks(*mark))

    if log:
        print("Успешное обновление Оценок")
        print("##########################")

    session.commit()

    if log:
        print("Успешно эмулирован новый день:", days[TODAY.weekday()], str(TODAY))
        print("##############################################")

    return "Успешно эмулирован новый день: " + days[TODAY.weekday()] + str(TODAY) + "\nДобавлены новые ДЗ и оценки"
