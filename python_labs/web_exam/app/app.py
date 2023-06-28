from flask import Flask, render_template, abort, send_from_directory, url_for, flash, redirect, request
from sqlalchemy import MetaData, distinct, desc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)
db = SQLAlchemy(app, metadata=metadata)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from book import bp as book_bp

app.register_blueprint(auth_bp)
app.register_blueprint(book_bp)

from models import Book, Genre, BookToGenre, Review, Cover
from tools import ImageSaver

init_login_manager(app)

@app.route('/')
def index():
    books = db.session.execute(db.select(Book)).scalars()
    genres = Genre.query.all()
    book_genre = BookToGenre.query.all()
    
    return render_template('index.html', books=books, genres=genres, book_genre=book_genre)

@app.route('/media/images/<cover_id>')
def image(cover_id):
    cover = Cover.query.get(cover_id)
    if cover is None:
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'], cover.file_name)

# @app.route('/book/create', methods=['GET', 'POST'])
# def create():
#     if request.method == 'GET':
#         genres = Genre.query.all()
#         return render_template('book/create.html', genres=genres)
    
#     if request.method == 'POST':
#         name = request.form.get('name')
#         description = request.form.get('description')
#         year = request.form.get('year')
#         publisher = request.form.get('publisher')
#         author = request.form.get('author')
#         pages = request.form.get('pages')
#         file = request.files.get('cover_img')

#         if file and file.filename:
#             try:
#                 cover_id = ImageSaver(file).save()
#                 book = Book(name=name, description=description, year=year, publisher=publisher, author=author, pages=pages, cover_id=cover_id)
#                 db.session.add(book)
#                 db.session.commit()
#                 genres = request.form.getlist('genre_id')
#                 for item in genres:
#                     b_to_g = BookToGenre(books_id=book.id, genres_id=item)
#                     db.session.add(b_to_g)
#                     db.session.commit()
#                 flash(f'Книга "{book.name}" успешно добавлена!', 'success')
#                 return redirect(url_for('index'))
#             except:
#                 flash("Возникла ошибка", "danger")
#                 return redirect(url_for('book/create'))
#         else:
#             flash("Добавьте файл изображения для обложки книги", "warning")
#             return redirect(url_for('book/create'))