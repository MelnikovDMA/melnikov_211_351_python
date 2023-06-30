from flask import Flask, render_template, abort, send_from_directory, url_for, flash, redirect, request
from flask_login import current_user
from sqlalchemy import MetaData, distinct, desc
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
import markdown
import math
from config import BOOKS_PER_PAGE
import datetime


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

from models import Book, Genre, BookToGenre, Cover, Visit, User

init_login_manager(app)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books_from_db = db.session.execute(db.select(Book).order_by(desc(Book.year)).limit(app.config['BOOKS_PER_PAGE']).offset(app.config['BOOKS_PER_PAGE'] * (page - 1))).scalars()
    books = []
    for book in books_from_db:
        book.description = markdown.markdown(book.description)
        books.append(book)
    book_count = Book.query.count()
    page_count = math.ceil(book_count / app.config['BOOKS_PER_PAGE'])
    genres = Genre.query.all()
    book_genre = BookToGenre.query.all()
    
    avg_list = []
    for cur_book in Book.query.all():
        reviews_for_book = cur_book.reviews
        rating = [review.rating for review in reviews_for_book]
        avg_rating = 0
        if len(rating) != 0: 
            avg_rating = sum(rating)/len(rating)
        avg_list.append(avg_rating)

    date_3_months = datetime.datetime.now() - datetime.timedelta(days=90)
    visits = db.session.execute(db.select(Visit.book_id).filter(Visit.created_at >= date_3_months).order_by(desc(func.count(Visit.book_id))).group_by(Visit.book_id).limit(5)).scalars()
    popular_books = []
    for visit in visits:
        pop_book = db.session.query(Book).filter(Book.id == int(visit)).scalar()
        popular_books.append(pop_book)

    recent_visits =  db.session.execute(db.select(Visit.book_id).filter(Visit.user_id==current_user.id).order_by(desc(Visit.created_at)).limit(5)).scalars()
    recent_viewed_books = []
    for visit in recent_visits:
        recent_book = db.session.query(Book).filter(Book.id == int(visit)).scalar()
        recent_viewed_books.append(recent_book)

    return render_template('index.html', books=books, genres=genres, book_genre=book_genre, page = page, page_count = page_count, avg_list=avg_list, popular_books=popular_books, recent_viewed_books=recent_viewed_books)

@app.route('/media/images/<image_id>')
def image(image_id):
    cover = Cover.query.get(image_id)
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