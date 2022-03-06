import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from making_db_structure import Schools, Subjects, Classes, Students, Studying, Hometasks, \
    Marks, Timetables, Base, Notes
from config import log

'''
Общение с БД
'''

# Session
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)  # Как только у вас появится engine
session = Session()


def set_tg_id(user_nickname, tg_id):
    user = session.query(Students).filter_by(nickname=user_nickname).first()
    user.tg_id = tg_id
    session.commit()
    return "Пользователь успешно авторизовался\nАккаунт дневника привязан к Telegram аккаунту"


def set_password(tg_id, new_password):
    user = session.query(Students).filter_by(tg_id=tg_id).first()
    user.password = new_password
    session.commit()
    return f'Пароль был изменен на {new_password}'


def set_info(tg_id, new_info):
    user = session.query(Students).filter_by(tg_id=tg_id).first()
    user.info = new_info
    session.commit()
    return f'Информация о вас была изменена на {new_info}'


def set_notes(tg_id, new_deal):
    user = session.query(Students).filter_by(tg_id=tg_id).first()
    todo = session.query(Notes).filter(Notes.student_id == user.id)
    c = 0
    for deal in todo:
        c = deal.order
    session.add(Notes(student_id=user.id, order=c + 1, note=new_deal))
    session.commit()
    return f'К вашим задачам на место {c + 1} был добавлен пункт {new_deal}'


def remove_tg_id(user_nickname):
    user = session.query(Students).filter_by(nickname=user_nickname).first()
    user.tg_id = ""
    session.commit()
    return "Пользователь успешно вышел\nАккаунт дневника больше не привязан к Telegram аккаунту"


def remove_note(tg_id, rm_id):
    user = session.query(Students).filter_by(tg_id=tg_id).first()
    d = get_note(user.nickname)
    out = "Удалены строки"
    deals_to_delete = []  # Список дел для удаления
    for i in rm_id.split():
        if i in ["ALL", "Clear", "clear", "all", "All", "CLEAR"]:
            todo = session.query(Notes).filter(Notes.student_id == user.id)
            for deal in todo:
                session.delete(deal)
            out = "Список дел был очищен"
        else:
            if not i.isnumeric() or not int(i) in d.keys():  # Проверка на правильность ввода
                if out == "Удалены строки":
                    return f"Нет {i} среди номеров задач!"
                else:
                    return out + f"\nНо нет {i} среди номеров задач!"
            else:
                todo = session.query(Notes).filter(Notes.order == i)
                for deal in todo:
                    deals_to_delete.append(deal)
                    out += " " + str(deal.order)

    for dd in deals_to_delete:
        session.delete(dd)

    c = 0  # Добавляение новой нумерации
    for deal in session.query(Notes).filter(Notes.student_id == user.id):
        c += 1
        deal.order = c
    session.commit()
    return out


def get_password(user_nickname):
    if user_nickname == "~~~random~~~":
        students = session.query(Students).all()
        p = [[i.nickname, i.password] for i in students]
        return random.choice(p)
    else:
        user = session.query(Students).filter_by(nickname=user_nickname).first()
        if user is None:
            return user
        else:
            return user.password


def get_note(user_nickname):
    user = session.query(Students).filter_by(nickname=user_nickname).first()
    todo = session.query(Notes).filter(Notes.student_id == user.id)
    deals = {}
    for deal in todo:
        deals[deal.order] = deal.note
    return deals


def get_info(user_nickname):
    user = session.query(Students).filter_by(nickname=user_nickname).first()
    if user is None:
        return user
    else:
        return user.info


def get_user_with_tg_id(tg_id):
    user = session.query(Students).filter_by(tg_id=tg_id).first()
    if user is None:
        return user
    else:
        return user.nickname


def get_subjects(tg_id):
    student = session.query(Students).filter_by(tg_id=tg_id).first()
    subjects_table = session.query(Studying).filter_by(student_id=student.id)
    subjects = []
    for row in subjects_table:
        subject_id = row.subject_id
        subjects.append(session.query(Subjects).filter_by(id=subject_id).first().name)

    return subjects


def get_marks(tg_id, subject="Все оценки"):
    r_s = subject
    d = False
    if subject == "Все оценки":
        d = True
    student = session.query(Students).filter_by(tg_id=tg_id).first()
    marks = {}
    lessons = session.query(Studying).filter(Studying.student_id == student.id)
    for lesson_id in lessons:
        lesson_id = lesson_id.subject_id
        lesson = session.query(Subjects).filter_by(id=lesson_id).first()
        marks.update([(lesson.name, [])])

    marks_tmp = session.query(Marks).filter(Marks.student_id == student.id)
    for row in marks_tmp:
        # print(row.subject)
        subject = row.subject[:row.subject.find("(") - 1]
        mark = row.mark
        date = row.date
        marks[subject].append([mark, date])

    if d:
        return marks
    else:
        return marks[r_s]


def get_hometask(tg_id, subject="Все задания"):
    d = False
    if subject == "Все задания":
        d = True
    student = session.query(Students).filter_by(tg_id=tg_id).first()
    timetable = session.query(Timetables).filter_by(student_id=student.id).first()

    hts = session.query(Hometasks).filter_by(timetable_id=timetable.id)
    hometasks = {}
    lessons = session.query(Studying).filter(Studying.student_id == student.id)
    for lesson_id in lessons:
        lesson_id = lesson_id.subject_id
        lesson = session.query(Subjects).filter_by(id=lesson_id).first()
        hometasks.update([(lesson.name, [])])

    for ht in hts:
        subject_name = ht.subject
        subject_name = subject_name[:subject_name.find("(") - 1]
        task = ht.task
        date = ht.date
        done = ht.done
        hometasks[subject_name].append([task, date, done])

    # сортировка по дате
    for lesson in hometasks:
        for mark1 in range(len(hometasks[lesson]) - 1):
            for mark2 in range(len(hometasks[lesson]) - mark1 - 1):
                if hometasks[lesson][mark2][1] > hometasks[lesson][mark2 + 1][1]:
                    hometasks[lesson][mark2], hometasks[lesson][mark2 + 1] = hometasks[lesson][mark2 + 1], \
                                                                             hometasks[lesson][mark2]

    if d:
        return hometasks
    else:
        return hometasks[subject]


def get_timetable(tg_id):
    student = session.query(Students).filter_by(tg_id=tg_id).first()
    timetable = session.query(Timetables).filter_by(student_id=student.id).first()
    return str(timetable.timetable)


def get_timetables_all():
    timetables = session.query(Timetables).all()
    tts = [i.tt for i in timetables]
    return tts


def get_tt(tg_id):
    student = session.query(Students).filter_by(tg_id=tg_id).first()
    timetable = session.query(Timetables).filter_by(student_id=student.id).first()
    return timetable.tt


def reduct_notes(tg_id, note=""):
    student = session.query(Students).filter_by(tg_id=tg_id).first()
    student.notes += note
    session.commit()
    return student.notes


# Вывод программы
if log:
    print("Успешный обмен данных с БД")
    print("##########################")
