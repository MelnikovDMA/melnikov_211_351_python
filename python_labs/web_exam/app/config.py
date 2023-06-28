import os

SECRET_KEY = 'abcdefg'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_1088_exam:webexam1088@std-mysql.ist.mospolytech.ru/std_1088_exam'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
