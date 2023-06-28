SECRET_KEY = 'e341e6698cb20dd889d040a9be7d5fc129cb06255f349bd6ea3f901afe8d61b4'

MYSQL_USER = 'std_1088_web_lab4'
MYSQL_PASSWORD = 'Xmelnikov1337'
MYSQL_HOST = 'std-mysql.ist.mospolytech.ru'
MYSQL_DATABASE = 'std_1088_web_lab4'

TYPES_OF_ERRORS = {
        "empty_login": "Поле логина не должен быть пустым",
        "empty_passwordd": "Поле пароля не должен быть пустым",
        "empty_last_name": "Поле фамилии не должен быть пустым",
        "empty_first_name": "Поле имени не должно быть пустым",
        "login_wrong_size": "Логин должен быть длины не меньше 5 символов",
        "login_wrong_chars": "Логин должен состоять только из латинских букв и цифр",
        "password_smallest_length": "Пароль должен быть длины не меньше 8 символов",
        "password_biggest_length": "Пароль должен быть длины не более 128 символов",
        "password_with_spaces": "Пароль не должен содержать пробелов",
        "password_wrong_chars": '''Пароль должен состоять из латинских или кириллических букв, содержать только арабские цифры и допустимые символы''',
        "password_not_upper_simbol": "Пароль должен содержать как минимум одну заглавную букву",
        "password_not_lower_simbol": "Пароль должен содержать как минимум одну строчную букву",
        "password_not_digit": "Пароль должен содержать как минимум одну цифру",
        "wrong_password": "Неверный пароль",
        "wrong_checked_password": "Пароль должен совпадать"
    }