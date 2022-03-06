import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import os.path
import tempfile
import pandas as pd
from random import randint
from config import log

'''
Реализация сложных функций: Рисование графиков, Предсказание будущей оценки, Варианты получения среднего балла и тд
'''


def prediction(*args):
    """
    Предсказания будущей оценки, вычисляеться средним арифметическим
    :param args: Оценки *[список оценок]
    :return: Возможная следующая оценка (Среднее арифметическое)
    """
    return round(sum(args) / len(args))


def graph(**marks):
    '''
    Построение графика оценок
    Params:
        **marks: {"<число>":<оценка>,...}
    !!! Необходимо передавать отсортированный по дате словарь collections.OrderedDict
    return:
        возвращает полный путь png файла с графиком
    '''

    fileName = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.png")
    series = pd.Series(marks)
    a = pd.DataFrame({'число': series.index, "оценки": series.values})
    sns.barplot(data=a, x='число', y="оценки")
    plt.savefig(fileName, format='png')
    # plt.show()  # Показывает сгенерированный график
    return fileName


def variants(target: int, days: int, count: int = 5, *marks):
    """
    Варианты получения желаемого среднего балла
    :param target: Средний балл к которому стремимся
    :param days: Количество оценок для изменения среднего балла
    :param count: Количество путей изменения среднего балла
    :param marks: Оценки, идущие друг за другом *[your_marks]
    :return: Список длинной count, в котором 1) список, содержащий вариант получения среднего балла и 2) Полученный балл
    """
    if target not in {1, 2, 3, 4, 5}: raise Exception("Bad target")
    if not isinstance(days, int) and days > 0: raise Exception("Bad days")
    if len(marks) == 0: raise Exception("Bad marks")

    result = list()
    for _ in range(count):
        _m = [i for i in marks]
        for day in range(days):
            _avg = sum(_m) / len(_m)
            if _avg == target:
                _min = round(_avg) - 1
                _max = round(_avg) + 1
            elif _avg < target:
                _min = round(_avg) + 1
                _max = 5
            else:
                _min = 1
                _max = round(_avg) - 1
            if _min < 1: _min = 1
            if _max > 5: _max = 5
            if _min > _max: _min, _max = _max, _min
            _m.append(randint(_min, _max))
        result.append([[str(i) for i in _m[len(marks):]], sum(_m) / len(_m)])
    return result


# # Вывод программы
# if log:
#     print("Успешное работа особой функции")
#     print("##############################")
