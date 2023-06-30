import os
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from users_policy import UsersPolicy
from flask import url_for
from app import db

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.String(100), db.ForeignKey("covers.id"), nullable=False)

    def __repr__(self):
        return '<Book %r>' % self.name
    
    def get_img(self):
        img = db.session.execute(db.select(Cover).filter_by(id=self.cover_id)).scalar()
        return img   

    def get_genres(self):
        genres_ids = db.session.execute(db.select(BookToGenre).filter_by(book_id=self.id)).all()
        if genres_ids:
            genres = []
            for genre_id in genres_ids:
                genre = db.session.execute(db.select(Genre).filter_by(id=genre_id[0].genre_id)).scalar()
                genre = genre.name
                genres.append(genre)
            return genres
    
    reviews = db.relationship('Review')
    bookstogenre = db.relationship('BookToGenre')
    cover = db.relationship('Cover')
    
class Cover(db.Model):
    __tablename__ = 'covers'

    id = db.Column(db.String(100), primary_key=True)
    file_name = db.Column(db.String(100), nullable=False)
    mime_type = db.Column(db.String(100), nullable=False)
    md5_hash = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return '<Cover %r>' % self.file_name
    
    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('image', image_id=self.id)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  
    text = db.Column(db.Text(), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

    def __repr__(self):
        return '<Review %r>' % self.text
    
    def get_user(self):
        return db.session.execute(db.select(User).filter_by(id=self.user_id)).scalar().login

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    password_hash = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def can(self, action, record=None):
        users_policy = UsersPolicy(record)
        method = getattr(users_policy, action, None)
        if method:
            return method()
        return False
    
    def is_admin(self):
        return self.role_id == 3
    
    def is_moder(self):
        return self.role_id == 2
    
    def __repr__(self):
        return '<User %r>' % self.login

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)

    def __repr__(self):
        return '<Role %r>' % self.name
    
class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

    def __repr__(self):
        return '<Genre %r>' % self.name
    
class BookToGenre(db.Model):
    __tablename__ = 'book_to_genres'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"), nullable=False)

    book = db.relationship('Book')
    genre = db.relationship('Genre')

class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    created_at = created_at = db.Column(db.DateTime, nullable=False, server_default=sa.sql.func.now())

