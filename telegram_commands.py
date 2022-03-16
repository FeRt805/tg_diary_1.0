import datetime
from config import TOKEN
from config import log, sasha1, admin
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.utils.markdown import text, bold, italic, code, pre
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions, InputFile
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from next_day import next_day
# pip3 install -r .\requirments.txt
from filling_db import generate, load
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from tg_table import marks_table, hometask_table, deals_list
from get_from_db import get_user_with_tg_id, set_tg_id, get_password, remove_tg_id, get_timetable, reduct_notes, \
    get_marks, get_subjects, get_hometask, set_password, set_info, get_info, get_note, set_notes, remove_note, get_tt
from complex_functions import prediction, graph, variants

from collections import OrderedDict

# TODO: hometask добавить возможность галочки, в презентацию добавить nextday, ограничение по символам на marks

'''
Главный файл, который должен непрерывно работать
Общение с пользователем Telegram
'''

# Все комманды бота, отсылаеться @BotFather
commands_f_b = \
    '''
start - Начало работы
help - Справка по функционалу бота
login - Вход в свою учетку
exit - Выход из своей учетки
password - Ваш пароль
info - Редактирование информации о себе
list - Редактируемый список дел
timetable - Расписание уроков
marks - Таблица оценок
hometask - Таблица с Д/З 
next - Следующий урок по времени
predict - Предсказание будущей оценки
get_mark- Поиск вариата получения желаемого среднего балла
graph - Динамика успеваемости
fill_db - Перезаполнение баззы данных (админ)
get_password - Запрос пароля у пользователя (админ)
next_day - Эмуляция прошедших дней (админ) 
'''

# Стартовый(приветственный) текст
description_f_b = \
    '''
Привет! 👋

Это бот для помощи в обучении и организации поставленных задач

👨‍💻Автор: @FeRt805 
'''

# Текст, показываемый по вызову команды /help
help_text = \
    '''
*Команды бота и пояснение к их функционалу*
_В скобках "()" указаны другие варианты написания команд_ 

/start - Проверка на вход 

/help - Справка по функционалу бота

/login - Вход в свою учетку

/exit - Выход из своей учетки

/password_(/pw)_ - Ваш пароль к учетке
_Пароль можно поменять_

/info_(/about_\\__me)_ - Редактирование информации о себе
_Информация о вашем аккаунте_

/list_(/todo; /deals)_ - Редактируемый список дел
_Задачи добавляються в конец списка_
_Чтобы очистить список ALL или clear_
_При окончании работы со списком напишите ~~~_

/timetable - Расписание уроков

/marks_(/grades)_ - Таблица оценок

/hometask_(/ht; /hw; /homework)_ - Таблица с Д/З 

/next - Следующий урок исходя из времени отправки сообщения

/predict(/pr) - Предсказание будущей оценки

/get\\_mark_(/gm)_ - Выводит способы получения желаемого среднего балла
_Например:_
_/get_\\__mark 10 7_
_Выводиться список возможных путей получения позже указаного среднего балла в количестве 7 длинной 10_ 

/graph_(/gr)_ - Визуализация динамики успеваемости


*Функции Администратора*
 
/fill\\_db_(/fill_\\__database)_ - Генерация новой БД (Новые ученики, оценки и т.д.)

/get\\_password - Получение пароля желаемого пользователя 
_/get_\\__password ~~~random~~~ выдает случайный логин и пароль_

/next\\_day - Эмулирует желаемое количество прошедших дней (добавляются ДЗ и оценки)
'''

days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

subjects = []
subj = []
admins_nicks = [sasha1[0], admin[0]]

way = 5
leng = 3
subject_f_a = "Русский язык"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class add_notes(StatesGroup):
    waiting_for_end = State()


class del_notes(StatesGroup):
    id_to_del = State()


class info_text(StatesGroup):
    about_me_text = State()


class ch_password(StatesGroup):
    new_password = State()


class dest_mark_wait(StatesGroup):
    dest_mark = State()

class wait_for_ht(StatesGroup):
    ht_subject = State()

class wait_for_pr(StatesGroup):
    args = State()

async def is_user_logined(tg_id, message):
    """
    Проверка пользователя на авторизацию
    :param tg_id:
    :param message:
    :return: True/False
    """
    if get_user_with_tg_id(tg_id) is None:
        await message.reply("Нужно авторизоваться, чтобы пользоваться этой функцией!\nИспользуйте /login")
        return False
    else:
        return True


########################################################################

@dp.message_handler(commands=['start'])
async def start_func(message: types.Message):
    sticker_welcome = "CAACAgIAAxkBAAIBUmHZlnyxlmgi2sOsLrPWPwNpKS3-AAKKAgACVp29Cj5SbosTxUBnIwQ"  # sticker tg id
    await bot.send_sticker(message.chat.id, sticker_welcome)

    tg_id = message.from_user.id
    nickname = get_user_with_tg_id(tg_id)

    if nickname is None:
        s = "Для начала, стоит попробовать авторизоваться используя команду " \
            "/login _username_ _password_"
    else:
        s = nickname + ", вы уже авторизовались и можете начать пользоваться функциями"

    await bot.send_message(message.chat.id, f"Привет, {message.from_user.full_name}! "
                                            "Это бот-дневник, который может помочь в обучении\n"
                           + s +
                           "\n\nЕсли что-то непонятно - попробуйте /help",
                           parse_mode=ParseMode.MARKDOWN)


########################################################################

@dp.message_handler(commands=['help'])
async def help_func(message: types.Message):
    await bot.send_message(message.chat.id, help_text, parse_mode=ParseMode.MARKDOWN)


########################################################################

@dp.message_handler(commands=['next'])
async def next_func(message: types.Message):
    """
    Отсылает на основе текущего времени следующий урок
    :param message:
    :return:
    """

    tg_id = message.from_user.id

    if await is_user_logined(tg_id, message):
        m_date = message.date

        tt = get_tt(tg_id)
        weekday = days[m_date.weekday()]
        m_date_time = m_date.time()
        m = True
        if weekday in tt:
            for lesson in tt[weekday]:
                lesson_start_time_str = lesson[lesson.find("(") + 1:lesson.find("-") - 1]
                lesson = lesson[:lesson.find("(")]
                l_t = datetime.datetime.strptime(lesson_start_time_str, "%H:%M")
                lesson_start_time = l_t.time()
                if m_date_time < lesson_start_time:
                    q1 = datetime.datetime.combine(datetime.date.today(), m_date_time)
                    q2 = datetime.datetime.combine(datetime.date.today(), lesson_start_time)
                    df = q2 - q1
                    await message.reply(f"Через {df} начнеться урок *{lesson}*в {lesson_start_time_str}",
                                        parse_mode=ParseMode.MARKDOWN)
                    m = False
                    break
            if m:
                await message.reply("Сегодня больше не будет уроков!", parse_mode=ParseMode.MARKDOWN)

        else:
            await message.reply("Сегодня уроков нет!", parse_mode=ParseMode.MARKDOWN)


########################################################################

inline_btn_1 = InlineKeyboardButton('Изменить пароль', callback_data='button1435435')
inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1)


@dp.message_handler(commands=['password'], state="*")
async def password_func(message: types.Message):
    """
    Пароль
    :param message:
    :return:
    """
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        t = f"Ваш текущий пароль:\n{get_password(get_user_with_tg_id(tg_id))}"
        await message.reply(t, reply_markup=inline_kb1)


@dp.callback_query_handler(lambda c: c.data == 'button1435435', state="*")
async def password_start(callback_query: types.CallbackQuery):
    """
    Меняеться пароль
    :param callback_query:
    :return:
    """
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите новый пароль:')
    await ch_password.new_password.set()


@dp.message_handler(state=ch_password.new_password)
async def password_chosen(message: types.Message, state: FSMContext):
    """
    Принимает присланное значение и меняет пароль
    :param message:
    :param state:
    :return:
    """
    await state.update_data(new_password=message.text)
    tg_id = message.from_user.id
    user_data = await state.get_data()
    await message.answer(set_password(tg_id, user_data["new_password"]))
    await state.finish()


########################################################################

inline_btn_2 = InlineKeyboardButton('Изменить информацию о себе', callback_data='button232314334')
inline_kb2 = InlineKeyboardMarkup().add(inline_btn_2)


@dp.message_handler(commands=["about_me", "info"], state="*")
async def about_me_func(message: types.Message):
    """
    Информация о пользователе
    :param message:
    :return:
    """
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        t = f"Текущая информация о вас:\n{get_info(get_user_with_tg_id(tg_id))}"
        await message.reply(t, reply_markup=inline_kb2)


@dp.callback_query_handler(lambda c: c.data == 'button232314334', state="*")
async def about_me_start(callback_query: types.CallbackQuery):
    """
    Менет информацию о пользователе
    :param callback_query:
    :return:
    """
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Введите информацию о вас')
    await info_text.about_me_text.set()


@dp.message_handler(state=info_text.about_me_text)
async def about_me_chosen(message: types.Message, state: FSMContext):
    """
    Принимает присланное значение и меняет информацию о пользователе
    :param message:
    :param state:
    :return:
    """
    await state.update_data(about_me_text=message.text)
    tg_id = message.from_user.id
    user_data = await state.get_data()
    await message.answer(set_info(tg_id, user_data["about_me_text"]))
    await state.finish()


########################################################################

inline_btn_3_1 = InlineKeyboardButton('Добавить задание', callback_data='button3433434341')
inline_btn_3_2 = InlineKeyboardButton('Удалить задание', callback_data='button3433434342')
inline_kb3 = InlineKeyboardMarkup().add(inline_btn_3_1).add(inline_btn_3_2)


@dp.message_handler(commands=['todo', "deals", "list"], state="*")
async def todo_func(message: types.Message):
    """
    Интерактивный список дел
    :param message:
    :return:
    """
    # Реализовать добавление одной строки вида /deals <строка на выполнение> <индекс?>

    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        q = deals_list(get_note(get_user_with_tg_id(tg_id)))
        t = f"Ваши текущие дела:\n{q}"
        if q == "\nУ вас пока нет никаких задач\n_Но вы можете добавить их, нажав на кнопку \n\"Добавить задание\"_":
            await message.reply(t, reply_markup=inline_kb3, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply(t, reply_markup=inline_kb3)


@dp.callback_query_handler(lambda c: c.data == 'button3433434341', state="*")
async def todo_add_start(callback_query: types.CallbackQuery):
    """
    Добавление новой задачи
    :param callback_query:
    :return:
    """
    await bot.answer_callback_query(callback_query.id)
    t = 'Введите новое задание:\n\n' + \
        "_Вы вошли в режим записок\n(с каждой новой строки идет новое задание)\nЧтобы выйти напишите ~~~_"
    await bot.send_message(callback_query.from_user.id, t,
                           parse_mode=ParseMode.MARKDOWN)
    await add_notes.waiting_for_end.set()


@dp.callback_query_handler(lambda c: c.data == 'button3433434342', state="*")
async def todo_remove_start(callback_query: types.CallbackQuery):
    """
    Удаление старой задачи
    :param callback_query:
    :return:
    """
    await bot.answer_callback_query(callback_query.id)
    t = 'Введите номер задания:\n\n' + \
        "_Вы вошли в режим удаления записок\n(удаляйте выполненые задания по индексу)\n" \
        "Вы можете прислать номера задач через пробел или просто с новой строки\nЧтобы выйти напишите ~~~_"
    await bot.send_message(callback_query.from_user.id, t,
                           parse_mode=ParseMode.MARKDOWN)

    await del_notes.id_to_del.set()


@dp.message_handler(state=del_notes.id_to_del)
async def todo_remove_chosen(message: types.Message, state: FSMContext):
    """
    Принимает присланное значение(индекс) и удалет задачу
    Чтобы выйти из режима записи ~~~
    :param message:
    :param state:
    :return:
    """
    await state.update_data(id_to_del=message.text)
    tg_id = message.from_user.id
    user_data = await state.get_data()
    if message.text != "~~~":
        if "/" in message.text:
            await message.answer("Возможно вы хотели выйти из режима удаления заметок"
                                 "\nПросто пришлите боту ~~~ для выхода")

        await message.answer(remove_note(tg_id, user_data["id_to_del"]) + "_\nЧтобы выйти пришлите ~~~_",
                             parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Вы вышли из режима удаления заметок\nМожете снова пользоваться функциями")
        await state.finish()


@dp.message_handler(state=add_notes.waiting_for_end)
async def todo_add_chosen(message: types.Message, state: FSMContext):
    """
    Принимает присланное значение и добавляет в конец списка задач
    Чтобы выйти из режима записи ~~~
    :param message:
    :param state:
    :return:
    """
    await state.update_data(waiting_for_end=message.text)
    tg_id = message.from_user.id
    user_data = await state.get_data()
    if message.text != "~~~":
        if "/" in message.text:
            await message.answer("Возможно вы хотели выйти из режима заметок\nПросто пришлите боту ~~~ для выхода")
        await message.answer(set_notes(tg_id, user_data["waiting_for_end"]) + "_\nЧтобы выйти пришлите ~~~_",
                             parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer("Вы вышли из режима заметок\nМожете снова пользоваться функциями")
        await state.finish()


########################################################################

@dp.message_handler(commands=['exit'])
async def exit_func(message: types.Message):
    """
    Выход из профиля из /login
    Деавторизация
    :param message:
    :return:
    """
    tg_id = message.from_user.id
    name = get_user_with_tg_id(tg_id)
    if name is None:
        photo = InputFile(r"./one_does_not_simply.jpg")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
    else:
        await bot.send_message(message.chat.id, remove_tg_id(name))


########################################################################
@dp.message_handler(commands=['next_day'])
async def nex_day_func(message: types.Message):
    # Эмуляция прошедших дней
    if len(message.text.split()) == 2:
        days_passed = message.text.split()[1]
        if days_passed.isnumeric():
            tg_id = message.from_user.id
            if get_user_with_tg_id(tg_id) in admins_nicks:
                await bot.send_message(message.chat.id, next_day(int(days_passed)))
            else:
                await message.reply("*У вас не достаточно прав чтобы выполнить эту команду!*",
                                    parse_mode=ParseMode.MARKDOWN)
        else:
            t = text(bold("Ошибка ввода"),
                     "\nВведите /next\\_day _количество дней для эмуляции_")

            await message.reply(t, parse_mode=ParseMode.MARKDOWN)

    else:
        t = text(bold("Ошибка ввода"),
                 "\nВведите /next\\_day _количество дней для эмуляции_")

        await message.reply(t, parse_mode=ParseMode.MARKDOWN)


########################################################################
@dp.message_handler(commands=['get_password'])
async def get_pass_func(message: types.Message):
    # Запрос пароля у пользователя
    if len(message.text.split()) == 2:
        nickname = message.text.split()[1]
        tg_id = message.from_user.id
        if get_user_with_tg_id(tg_id) in admins_nicks:
            await bot.send_message(message.chat.id, get_password(nickname))
        else:
            await message.reply("*У вас не достаточно прав чтобы выполнить эту команду!*",
                                parse_mode=ParseMode.MARKDOWN)
    else:
        t = text(bold("Ошибка ввода"),
                 "\nВведите /get\\_password _никнейм_\n~~~random~~~ для случайного логина и пароля")

        await message.reply(t, parse_mode=ParseMode.MARKDOWN)


########################################################################
@dp.message_handler(commands=['fill_db', 'fill_database'])
async def get_pass_func(message: types.Message):
    # Перезаполняет базу данных
    tg_id = message.from_user.id
    if get_user_with_tg_id(tg_id) in admins_nicks:
        await bot.send_message(message.chat.id, "Начало генерации данных")
        generate()
        await bot.send_message(message.chat.id, "Данные сгенерированы")
        await bot.send_message(message.chat.id, "Начало заполнения БД")
        load()
        await bot.send_message(message.chat.id, "БД была обновлена")
    else:
        await message.reply("*У вас не достаточно прав чтобы выполнить эту команду!*",
                            parse_mode=ParseMode.MARKDOWN)


########################################################################
@dp.message_handler(commands=['predict', "pr"])
async def predict_func(message: types.Message):
    """
    Предсказание будущей оценки
    :param message:
    :return:
    """
    global subjects, subj
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        subjects = get_subjects(tg_id)
        s = []
        # КОСТЫЛЬ заключающийся в добавлении пустого символа, который потом ищется хендлиром для обработки кнопок
        for i in subjects:
            # s.append(str(i) + " ")  # Невидимый символ
            s.append(str(i))  # Невидимый символ
        #      🔎 🔍 ☃☃☃☃
        subjects = s

        # Создаем кнопки
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        l = []

        for i in subjects:
            l.append(i)
            le = len(l)
            if i == subjects[-1]:
                kb.row(*l)
                le = -1
            if le == 3:
                kb.row(*l)
                l = []

        marks = "Выберите предмет..."
        await wait_for_pr.args.set()
        await message.answer(marks, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


########################################################################
@dp.message_handler(state=wait_for_pr.args)
async def predict_handle(message: types.Message, state: FSMContext):
    """
    Обработчик предсказаний
    """
    await state.update_data(args=message.text)
    tg_id = message.from_user.id
    user_data = await state.get_data()
    if await is_user_logined(tg_id, message):
        marks = get_marks(tg_id, message.text)

        # сортировка по дате
        for mark1 in range(len(marks) - 1):
            for mark2 in range(len(marks) - mark1 - 1):
                if marks[mark2][1] > marks[mark2 + 1][1]:
                    marks[mark2], marks[mark2 + 1] = marks[mark2 + 1], marks[mark2]

        pretty_marks = "```" + marks_table(marks, message.text) + "```"
        raw_marks = []
        for i in marks:
            raw_marks.append(i[0])

        if len(raw_marks) == 0:
            predict = "У вас нет оценок по этому предмету"
        else:
            predict = "Похоже, что следущая оценка: " + str(prediction(*raw_marks))
        await bot.send_message(message.chat.id, pretty_marks,
                               reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)

        await bot.send_message(message.chat.id, predict,
                               reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)
        await state.finish()

########################################################################


@dp.message_handler(commands=['get_mark', "gm"])
async def variants_func(message: types.Message):
    """
    Поиск варианта оценок для достижения запрошенного среднего балла
    :param message:
    :return:
    """
    q = True  # Для проверки на ввод пользователя
    if len(message.text.split()) == 3:

        d = message.text.split()[1]  # Количество оценок пути
        lng = message.text.split()[2]  # Количество вариатов

        if d.isnumeric() and lng.isnumeric():
            q = False
            t = text(bold("Значения указаны неверно!"), "Cм. /help")
            await message.reply(t, parse_mode=ParseMode.MARKDOWN)

    else:

        t = text("Не указаны значения \"кол-во оценок\" и \"кол-во вариатов\""
                 "\nВзяты значения 5 и 3\nСм. /help ")
        d = "5"  # кол-во оценок
        lng = "3"  # кол-во вариатов
        await message.reply(t, parse_mode=ParseMode.MARKDOWN)

    # Выбор предмета
    if q:
        global subjects, subj
        tg_id = message.from_user.id
        if await is_user_logined(tg_id, message):
            subjects = get_subjects(tg_id)

            keyboard = InlineKeyboardMarkup(row_width=3)

            # Создаем кнопки
            l = []
            for i in subjects:
                l.append(InlineKeyboardButton(i, callback_data="var_but" + "?" + i + "?" + d + "?" + lng))

            keyboard.add(*l)

            await message.answer("Выберите предмет...", reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)


########################################################################
@dp.callback_query_handler(text_contains="var_but")
async def variant_chosen(call: types.CallbackQuery):
    """
    Выбор желаемого среднего балла дл функции поиска вариатов
    :param call:
    :return:
    """
    global way, leng, subject_f_a

    q = call.data.split("?")
    subject_f_a = q[1]
    way = q[2]
    leng = q[3]

    await call.answer(text=f"Вы выбрали \"{subject_f_a}\"", show_alert=True)

    await call.message.answer(text="Выберите средний балл, который хотите получить...\n_Число от 3 до 5_",
                              parse_mode=ParseMode.MARKDOWN)

    await dest_mark_wait.dest_mark.set()


@dp.message_handler(state=dest_mark_wait.dest_mark)
async def variant_mark_chosen(message: types.Message, state: FSMContext):
    """
    Обработчик функции поиска вариатов
    :param message:
    :param state:
    :return:
    """
    await state.update_data(id_to_del=message.text)
    user_data = await state.get_data()
    tg_id = message.from_user.id
    if message.text in ["3", "4", "5"]:
        global way, leng, subject_f_a
        marks_f = get_marks(tg_id, subject_f_a)
        marks = [i[0] for i in marks_f]
        marks_out = [str(i[0]) + " " for i in marks_f]
        dest_mark = user_data["id_to_del"]
        await message.answer(text=f"Ваши текущие оценки по \"{subject_f_a}\":\n"
                                  + "".join(marks_out), parse_mode=ParseMode.MARKDOWN)
        if len(marks) != 0:
            k = 1
            for w in variants(int(dest_mark), int(way), int(leng), *marks):
                marks_way = [i + " " for i in w[0]]
                mark_average = w[1]
                t = f"Способ №{str(k)}\nВам нужно получить:\n" + "".join(marks_way) + \
                    f"\nВаш средний балл станет {str(mark_average)}"
                await message.answer(text=t, parse_mode=ParseMode.MARKDOWN)
                k += 1

        else:
            await message.answer(text="*Не хватает оценок!*", parse_mode=ParseMode.MARKDOWN)

        await state.finish()

    else:
        await message.answer(text="*Неверный ввод!*\nВыберите средний балл, который хотите получить...\n"
                                  "_Число от 3 до 5_", parse_mode=ParseMode.MARKDOWN)


########################################################################


@dp.message_handler(commands=['graph', "gr"])
async def graph_func(message: types.Message):
    """
    Отрисовка динамики успеваемости в виде графика
    :param message:
    :return:
    """
    global subjects, subj
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        subjects = get_subjects(tg_id)
        s = []
        # КОСТЫЛЬ заключающийся в добавлении пустого символа, который потом ищется хендлиром для обработки кнопок
        for i in subjects:
            s.append(str(i) + "📊")  # Невидимый символ
        #      🔎 🔍 ☃☃☃☃
        subjects = s

        # Создаем кнопки
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        l = []

        for i in subjects:
            l.append(i)
            le = len(l)
            if i == subjects[-1]:
                kb.row(*l)
                le = -1
            if le == 3:
                kb.row(*l)
                l = []

        marks = "Выберите предмет..."
        await message.answer(marks, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


########################################################################
@dp.message_handler(Text(contains="📊"))
async def predict_handle(message: types.Message):
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        marks = get_marks(tg_id, message.text[:-1])

        # сортировка по дате
        for mark1 in range(len(marks) - 1):
            for mark2 in range(len(marks) - mark1 - 1):
                if marks[mark2][1] > marks[mark2 + 1][1]:
                    marks[mark2], marks[mark2 + 1] = marks[mark2 + 1], marks[mark2]

        pretty_marks = "```" + marks_table(marks, message.text[:-1]) + "```"

        # Оценки
        await bot.send_message(message.chat.id, pretty_marks,
                               reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)

        raw_marks = OrderedDict()
        k = 0
        for i in marks:
            x = i[1].strftime('%d.%m') + k * " "  # Делаем уникальным ключи
            y = i[0]
            raw_marks.update({x: y})
            k += 1

        if len(raw_marks) == 0:
            t = "У вас нет оценок по этому предмету"
            await bot.send_message(message.chat.id, t,
                                   reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)
        else:
            f = graph(**raw_marks)
            photo = InputFile(f)
            await bot.send_photo(chat_id=message.chat.id, photo=photo)

            t = f"Выведена статистика по предмету \"{message.text[:-1]}\" за " \
                f"{list(raw_marks.keys())[0]} - {list(raw_marks.keys())[-1]}"
            await bot.send_message(message.chat.id, t,
                                   reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)


########################################################################


@dp.message_handler(commands=['timetable'])
async def timetable_func(message: types.Message):
    """
    Вывод расписания пользователя
    :param message:
    :return:
    """
    tg_id = message.from_user.id

    if await is_user_logined(tg_id, message):
        table = "```" + get_timetable(tg_id) + "```"
        await bot.send_message(message.chat.id, table, parse_mode=ParseMode.MARKDOWN)


########################################################################

@dp.message_handler(commands=['login'])
async def login_func(message: types.Message):
    # Запись tg username и tg id в базу данных для будущего индифицирования пользователя
    if len(message.text.split()) == 3:
        name = message.text.split()[1]
        password = message.text.split()[2]
        tg_id = message.from_user.id

        if password == get_password(name):
            await bot.send_message(message.chat.id, set_tg_id(name, tg_id))
        else:
            await message.reply("*Неправильный логин или пароль!*", parse_mode=ParseMode.MARKDOWN)

    else:

        t = text(bold("Ошибка ввода"),
                 "\nВведите свой логин и пароль через пробел, после комманды login \n\nНапример: /login vasya\_pupkin "
                 "password")

        await message.reply(t, parse_mode=ParseMode.MARKDOWN)


########################################################################

@dp.message_handler(commands=['marks', "grades"])
async def marks_func(message: types.Message):
    """
    Вывод оценок пользователя
    :param message:
    :return:
    """
    global subjects, subj
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        subjects = get_subjects(tg_id)
        s = []
        # КОСТЫЛЬ заключающийся в добавлении пустого символа, который потом ищется хендлиром для обработки кнопок
        for i in subjects:
            s.append(str(i) + "⁣")  # Невидимый символ
        #      🔎 🔍 ☃☃☃☃
        subjects = s

        # Создаем кнопки
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        l = []

        for i in subjects:
            l.append(i)
            le = len(l)
            if i == subjects[-1]:
                kb.row(*l)
                le = -1
            if le == 3:
                kb.row(*l)
                l = []

        kb.row(KeyboardButton("Все оценки⁣"))

        marks = "Выберите предмет..."
        await message.answer(marks, reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


########################################################################


@dp.message_handler(commands=['hometask', 'hometasks', "ht", "homework", "hw"])
async def hometasks_func(message: types.Message):
    """
    Вывод домашнего задания(дз) пользователя
    :param message:
    :return:
    """
    global subjects, subj
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        subjects = get_subjects(tg_id)
        s = []
        # КОСТЫЛЬ заключающийся в добавлении пустого символа, который потом ищется хендлиром для обработки кнопок
        # Я ПОЧИНИЛ ПОТОМУ ЧТО СРАНЫЙ EDGE не поддерживает этот символ
        for i in subjects:
            s.append(str(i))  # Невидимый символ
            # s.append(str(i) + " ")  # Невидимый символ
        #      🔎 🔍 ☃☃☃☃
        subjects = s

        # Создаем кнопки
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        l = []

        for i in subjects:
            l.append(i)
            le = len(l)
            if i == subjects[-1]:
                kb.row(*l)
                le = -1
            if le == 3:
                kb.row(*l)
                l = []

        # kb.add(*subjects)
        # kb.row(KeyboardButton("Все задания "))
        kb.row(KeyboardButton("Все задания"))
        await wait_for_ht.ht_subject.set()
        await message.answer("Выберите предмет...", reply_markup=kb, parse_mode=ParseMode.MARKDOWN)


########################################################################

@dp.message_handler(Text(contains="⁣"))
async def marks_handle(message: types.Message):
    """
    Обработчик вывода оценок
    :param message:
    :return:
    """
    tg_id = message.from_user.id
    if await is_user_logined(tg_id, message):
        marks = get_marks(tg_id, message.text[:-1])

        if len(marks) == 0:
            if message.text[:-1] == "Все оценки":
                pretty_marks = "У вас нет оценок по всем предметам\n_Удивительно!_"
            else:
                pretty_marks = f"У вас нет оценок по предмету \"{message.text[:-1]}\""
        else:
            pretty_marks = "```" + marks_table(marks, message.text[:-1]) + "```"

        await bot.send_message(message.chat.id, pretty_marks,
                               reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)


@dp.message_handler(state=wait_for_ht.ht_subject)
async def hometasks_handle(message: types.Message, state: FSMContext):
    """
    Обработчик вывода дз
    """
    await state.update_data(ht_subject=message.text)
    tg_id = message.from_user.id
    user_data = await state.get_data()
    if await is_user_logined(tg_id, message):
        hometask = get_hometask(tg_id, message.text)
        if len(hometask) == 0:
            if message.text == "Все задания":
                pretty_hometask = "У вас нет совершенно нет домашних заданий\n_Удивительно!_"
            else:
                pretty_hometask = f"У вас нет Д/З по предмету \"{message.text}\""
        else:
            pretty_hometask = "```" + hometask_table(hometask, message.text) + "```"

        # Лимит символов
        if len(pretty_hometask) > 4000:
            for lesson in get_subjects(tg_id):
                hometask = get_hometask(tg_id, lesson)
                if len(hometask) == 0:
                    pretty_hometask = f"У вас нет Д/З по предмету \"{lesson}\""
                else:
                    pretty_hometask = "```" + hometask_table(hometask, lesson) + "```"

                await bot.send_message(message.chat.id, pretty_hometask,
                                       reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)
        else:
            await bot.send_message(message.chat.id, pretty_hometask,
                                   reply_markup=types.ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)
    await state.finish()

# Запуск работы бота
if __name__ == '__main__':
    # Вывод программы
    if log:
        print("Начало функционирования Telegram бота")
        print("#####################################")

    executor.start_polling(dp)  # Запуск процесса TG бота

    # Вывод программы
    if log:
        print("Конец функционирования Telegram бота")
        print("####################################")
