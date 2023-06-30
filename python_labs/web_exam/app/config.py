import os

SECRET_KEY = 'supersecretkey'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_1088_exam2:webexam1088@std-mysql.ist.mospolytech.ru/std_1088_exam2'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
BOOKS_PER_PAGE = 2