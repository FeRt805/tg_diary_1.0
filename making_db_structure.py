from sqlalchemy import Column, Integer, String, create_engine, ForeignKey, DateTime, Boolean, PickleType
from sqlalchemy.ext.declarative import declarative_base
from config import log

'''
Создание структуры базы данных
'''

# ":memory:"
engine = create_engine('sqlite:///data.db', echo=False)

Base = declarative_base()


class Schools(Base):
    __tablename__ = 'schools'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Schools('%s')>" % self.name


class Classes(Base):
    __tablename__ = 'classes'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    school_id = Column(Integer, ForeignKey('schools.id'))

    def __init__(self, name, school_id):
        self.name = name
        self.school_id = school_id

    def __repr__(self):
        return "<Classes('%s','%s')>" % (self.name, self.school_id)


class Subjects(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Subjects('%s')>" % self.name


class Notes(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    order = Column(Integer)
    note = Column(String)

    def __init__(self, student_id, order, note):
        self.student_id = student_id
        self.order = order
        self.note = note

    def __repr__(self):
        return "<Notes('%s','%s', '%s')>" % (self.student_id, self.order, self.note)


class Students(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    password = Column(String)
    class_id = Column(Integer, ForeignKey('classes.id'))
    info = Column(String)
    tg_id = Column(String)
    notes = Column(String)

    def __init__(self, nickname, password, class_id, info, tg_id, notes):
        self.nickname = nickname
        self.password = password
        self.class_id = class_id
        self.info = info
        self.tg_id = tg_id
        self.notes = notes

    def __repr__(self):
        return "<Students('%s','%s','%s','%s','%s', '%s')>" % (self.nickname, self.password,
                                                               self.class_id, self.info,
                                                               self.tg_id, self.notes)


class Hometasks(Base):
    __tablename__ = 'hometasks'
    id = Column(Integer, primary_key=True)
    timetable_id = Column(Integer, ForeignKey('timetables.id'))
    subject = Column(String)
    task = Column(String)
    date = Column(DateTime)
    done = Column(Boolean)

    def __init__(self, timetable_id, subject, task, date, done):
        self.timetable_id = timetable_id
        self.subject = subject
        self.task = task
        self.date = date
        self.done = done

    def __repr__(self):
        return "<Hometasks('%s','%s','%s','%s', '%s')>" % (self.timetable_id, self.subject,
                                                           self.task, self.date, self.done)


class Marks(Base):
    __tablename__ = 'marks'
    id = Column(Integer, primary_key=True)
    timetable_id = Column(Integer, ForeignKey('timetables.id'))
    subject = Column(String)
    student_id = Column(Integer, ForeignKey('students.id'))
    mark = Column(Integer)
    date = Column(DateTime)

    def __init__(self, timetable_id, subject, student_id, mark, date):
        self.timetable_id = timetable_id
        self.subject = subject
        self.student_id = student_id
        self.mark = mark
        self.date = date

    def __repr__(self):
        return "<Marks('%s','%s','%s','%s', '%s')>" % (self.timetable_id, self.subject,
                                                       self.student_id, self.mark, self.date)


class Studying(Base):
    __tablename__ = 'studying'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    def __init__(self, student_id, subject_id):
        self.student_id = student_id
        self.subject_id = subject_id

    def __repr__(self):
        return "<Studying('%s','%s')>" % (self.student_id, self.subject_id)


class Timetables(Base):
    __tablename__ = 'timetables'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    timetable = Column(String)
    tt = Column(PickleType)

    def __init__(self, student_id, timetable, tt):
        self.student_id = student_id
        self.timetable = timetable
        self.tt = tt

    def __repr__(self):
        return "<Timetables('%s','%s','%s')>" % (self.student_id, self.timetable, self.tt)


# Создание таблицы
Base.metadata.create_all(engine)

# Вывод программы
if log:
    print("Успешное подключение к БД")
    print("#########################")

