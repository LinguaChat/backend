"""Общие константы проекта."""

# Выбор пола пользователя на сайте
GENDERS = (
    ('Male', 'Мужской'),
    ('Female', 'Женский'),
)

# Уровни владения языком
LANGUAGE_SKILL_LEVELS = (
    ('Newbie', 'Новичок'),
    ('Amateur', 'Любитель'),
    ('Profi', 'Профи'),
    ('Expert', 'Эксперт'),
    ('Guru', 'Гуру'),
)

# Ограничение по кол-ву родных и изучаемых языков
MAX_FOREIGN_LANGUAGES = 5
MAX_NATIVE_LANGUAGES = 3

# Ограничения в длине полей пользователя
EMAIL_MAX_LENGTH = 30
USERNAME_MAX_LENGTH = 12
PASSWORD_MAX_LENGTH = 12
MIN_AGE = 18
MAX_AGE = 60

LANGS_SORTING_VALS = {
    "En": 3,
    "Ru": 2,
    "Fr": 2,
    "De": 2,
    "It": 2,
    "Ja": 2,
    "Ko": 2,
    "Es": 2,
    "Tr": 1,
    "Ar": 1,
    "Nl": 1,
    "Ro": 1,
}
