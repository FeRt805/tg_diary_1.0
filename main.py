import os
import sys
import importlib.util

def check_module(module_name):
    """
    Проверяет, можно ли импортировать модуль без его фактического импорта
    """
    module_name = module_name.replace("-", "_")
    if module_name == "python_dateutil":
        module_name = "dateutil"

    if module_name == "pyyaml":
        module_name = "yaml"

    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        # print('Module: {} not found'.format(module_name))
        return None
    else:
        # print('Module: {} can be imported!'.format(module_name))
        return module_spec

# def check_module(module):
#     try:
#         importlib.import_module(module)
#         return True
#     except:
#         return None


with open("./requirments.txt", "r") as t:
    out = ""
    l = t.readlines()
    ll = [i[:i.find("=")] for i in l if i != "\n"]
    l_no = []
    for module in ll:
        if check_module(module) is None:
            q = ll.index(module)
            l_no.append(l[q])
            out += "Не удалось импортировать модуль: " + l[q] + "\n"
            # os.system("python3.9 -m pip install {}".format(l[q]))
    t.close()

if len(l_no) != 0:
    print(out)
    print("Попытка установки")
    os.system("python3.9 -m pip install -r requirments.txt")
    print("Установка завершена")
    l_no = []
    out = ""
    for module in ll:
        if check_module(module) is None:
            q = ll.index(module)
            l_no.append(l[q])
            out += "Не удалось импортировать модуль: " + l[q] + "\n"
    if len(l_no) != 0:
        print(out)
        print("Попробуйте\npython3.9 -m pip install -r requirments.txt")
        print("Выход...")
        sys.exit(1)


if not os.path.exists(r"./data.db"):  # Проверка на существование БД
    from filling_db import generate, load
    print("\nНе существует базы данных. Запуск процесса генерации\n")
    os.system("python3.9 ./making_db_structure.py")
    generate()
    load()
    print("\nБД сгенерирована\n")

print("\nЗапуск Telegram обработчика\n")
os.system("python3.9 ./telegram_commands.py")
