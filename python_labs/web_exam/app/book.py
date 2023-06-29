from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from auth import check_rights
import os
import markdown

bp = Blueprint('book', __name__, url_prefix='/book')

from models import Book, Genre, BookToGenre, Cover, Review
from tools import ImageSaver

@bp.route('/show/<int:book_id>')
def show(book_id):
    current_book = Book.query.get(book_id)
    current_book.description = markdown.markdown(current_book.description)
    book_genre = BookToGenre.query.all()
    cover_id = current_book.cover_id
    img = Cover.query.filter_by(id=cover_id).first()
    img = img.url
    if current_user.is_authenticated:
        review = Review.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    else:
        review = False
    reviews = Review.query.filter_by(book_id=book_id).all()

    review_arr = []
    if reviews:
        for item in reviews:
            review_arr.append({
                'get_user': item.get_user,
                'rating': item.rating,
                'text': item.text
            })
    return render_template('book/show.html', current_book=current_book, book_genre=book_genre, img=img, review=review, reviews=review_arr)

@bp.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        genres = db.session.execute(db.select(Genre)).scalars()
        return render_template('book/create.html', genres=genres)
    
    if request.method == 'POST':
        name = request.form.get('bookName')
        description = request.form.get('description')
        year = request.form.get('year')
        publisher = request.form.get('publisher')
        author = request.form.get('authorName')
        pages = request.form.get('pages')
        file = request.files.get('cover_img')

        if file and file.filename:
            try:
                cover_id = ImageSaver(file).save().id
                book = Book(name=name, description=description, year=year, publisher=publisher, author=author, pages=pages, cover_id=cover_id)
                db.session.add(book)
                db.session.commit()
                genres = request.form.getlist('genre_id')
                for item in genres:
                    b_to_g = BookToGenre(book_id=book.id, genre_id=item)
                    db.session.add(b_to_g)
                    db.session.commit()
                flash(f'Книга "{book.name}" успешно добавлена!', 'success')
                return redirect(url_for('index'))
            except:
                flash("Возникла ошибка", "danger")
                return redirect(url_for('book.create'))
        else:
            flash("Добавьте файл изображения для обложки книги", "warning")
            return redirect(url_for('book.create'))
        
@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
def edit(book_id):
    book = db.session.execute(db.select(Book).filter_by(id=book_id)).scalar()
    genres = db.session.execute(db.select(Genre)).scalars()
    if request.method == 'GET':
        selected_genres = BookToGenre.query.filter_by(book_id=book_id).all()
        list_of_genres = []
        for genre in selected_genres:
            list_of_genres.append(genre.genre_id)
        return render_template('book/edit.html', book=book, genres=genres, list_of_genres=list_of_genres)
    if request.method == 'POST':
        try:
            book.name = request.form.get('bookName')
            book.description = request.form.get('description')
            book.year = request.form.get('year')
            book.author = request.form.get('authorName')
            book.publisher = request.form.get('publisher')
            book.pages = request.form.get('pages')

            db.session.commit()
            while BookToGenre.query.filter_by(book_id=book_id).first():
                db.session.delete(BookToGenre.query.filter_by(book_id=book_id).first())
                db.session.commit()
            selected_genres = request.form.getlist('genre_id')
            for genre in selected_genres:
                b_to_g = BookToGenre(book_id=book_id, genre_id=genre)
                db.session.add(b_to_g)
                db.session.commit()
            flash(f'Книга "{book.name}" успешно изменена!', 'success')
            return redirect(url_for('index'))
        except:
            flash('Возникла ошибка', 'danger')
            return render_template('book/edit.html', book=book, genres=genres, list_of_genres=list_of_genres)
        
@bp.route('/<int:book_id>/delete', methods=['POST', 'GET'])
def delete(book_id):
    if request.method == 'POST':
        book_genres = BookToGenre.query.filter_by(book_id=book_id).all()
        for book_genre in book_genres:
            db.session.delete(book_genre)
            db.session.commit()
        book_reviews = Review.query.filter_by(book_id=book_id).all()
        for review in book_reviews:
            db.session.delete(review)
            db.session.commit()
        book = Book.query.filter_by(id=book_id).first()
        try:
            img = Cover.query.filter_by(id=book.cover_id).first()
            if len(Book.query.filter_by(cover_id=book.cover_id).all()) == 1:
                img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images', img.file_name)
                os.remove(img_path)
                db.session.delete(img)
                db.session.commit()
            else:
                db.session.delete(book)
                db.session.commit()
        except:
            pass
        flash(f'Книга успешно удалена!', 'success')
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))
    
@bp.route('/<int:book_id>/review', methods=['GET', 'POST'])
@login_required
def review(book_id):
    book = Book.query.get(book_id)
    if request.method == 'POST':
        text = request.form.get('review')
        grade = int(request.form.get('grade'))
        review = Review(rating=grade, text=text, book_id=book_id, user_id=current_user.get_id())
        db.session.add(review)
        db.session.commit()
        flash(f'Отзыв был успешно добавлен!', 'success')
        return redirect(url_for('book.show', book_id=book.id))
    if request.method == 'GET':
        return render_template('book/review.html', book=book)