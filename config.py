import yaml

path_to_config = r'../config.yaml'  # Конфиг с паролями и токеном


def get_config():
    with open(path_to_config) as f:
        return yaml.safe_load(f)


CONFIG = get_config()

log = CONFIG["log"]

sasha1 = CONFIG["sasha1"]
admin = CONFIG["admin"]

TOKEN = CONFIG["TOKEN"]

schools_num_min = CONFIG["schools_num_min"]
schools_num_max = CONFIG["schools_num_max"]

classes_to_remove_min = CONFIG["classes_to_remove_min"]
classes_to_remove_max = CONFIG["classes_to_remove_max"]

students_in_class_min = CONFIG["students_in_class_min"]
students_in_class_max = CONFIG["students_in_class_max"]

marks_chance_min = CONFIG["marks_chance_min"]
marks_chance_max = CONFIG["marks_chance_max"]
marks_chance_edge = CONFIG["marks_chance_edge"]
