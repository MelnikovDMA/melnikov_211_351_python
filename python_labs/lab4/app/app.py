from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from mysql_db import MySQL
from config import TYPES_OF_ERRORS
import mysql.connector

app = Flask(__name__)
application = app

PERMITTED_PARAMS = ["login", "password", "last_name", "first_name", "middle_name", "role_id"]

app.config.from_pyfile('config.py')
db = MySQL(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице необходимо пройти процедуру аутентификации.'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id, login):
        self.id = id
        self.login = login
        

@app.route('/')
def index():
    return render_template('index.html')

def authentificate_user(login, password):
    query = "SELECT * FROM users WHERE login = %s AND password_hash	= SHA2(%s, 256);"
    # query = f"SELECT * FROM users WHERE login = '{login}' AND password_hash = SHA2('{password}', 256);"
    #  user' OR 0=0#  password
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query, (login, password))
        # cursor.execute(query)
        print(cursor.statement)
        db_user = cursor.fetchone()
    if db_user is not None:
        user = User(db_user.id, db_user.login)
        return user
    return None

@login_manager.user_loader
def load_user(user_id):
    query = "SELECT * FROM users WHERE id = %s;"
    cursor = db.connection.cursor(named_tuple = True)
    cursor.execute(query, (user_id,))
    db_user = cursor.fetchone()
    cursor.close()
    if db_user is not None:
        user = User(user_id, db_user.login)
        return user
    return None

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == "POST":
        user_login = request.form["loginInput"]
        user_password = request.form["passwordInput"]
        remember_me = request.form.get('remember_me') == 'on'


        auth_user = authentificate_user(user_login, user_password)
        if auth_user:
            login_user(auth_user, remember=remember_me)
            flash("Вы успешно авторизованы", "success")
            next_ = request.args.get('next')
            return redirect(next_ or url_for("index"))
            
        flash("Введены неверные логин и/или пароль", "danger") 


    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/users')
def users():
    query = "SELECT users.*, roles.name as role_name FROM users LEFT JOIN roles on users.role_id=roles.id;"
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query)
        print(cursor.statement)
        db_users = cursor.fetchall()
    return render_template('users/index.html', users = db_users)

def load_roles():
    query = "SELECT * FROM roles;"
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(query)
        db_roles = cursor.fetchall()
    return db_roles

@app.route('/users/new')
@login_required
def new_user():
    return render_template('users/new.html', roles = load_roles(), user={}, errors={})

def insert_to_db(params):
    query = """
        INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) 
        VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);
    """
    try:
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(query, params)
            db.connection.commit()
    except mysql.connector.errors.DatabaseError:
        db.connection.rollback()
        return False

    return True

def validation_edit(params):
    PERMITTED_CHARS_OF_LOGIN = "1234567890abcdefghijklmnopqrstuvwxyz"
    error_list = {
        "login": None,
        "last_name": None,
        "first_name": None,
        "error_check": 1,
    }
    login = params.get("login")
    if login is None:
        error_list["login"] = TYPES_OF_ERRORS["empty_login"]
        error_list["error_check"] = 0
    elif len(login) < 5:
        error_list["login"] = TYPES_OF_ERRORS["login_wrong_size"]
        error_list["error_check"] = 0
    else:
        for char in login:
             if PERMITTED_CHARS_OF_LOGIN.find(char.lower()) == -1:
                 error_list["login"] = TYPES_OF_ERRORS["login_wrong_chars"]
                 error_list["error_check"] = 0
                 break

    if params.get("first_name") is None:
        error_list["first_name"] = TYPES_OF_ERRORS["empty_first_name"]
        error_list["error_check"] = 0

    if params.get("last_name") is None:
        error_list["last_name"] = TYPES_OF_ERRORS["empty_last_name"]
        error_list["error_check"] = 0

    return error_list

def check_password(params, PERMITTED_CHARS_OF_PASSWORD):
    error_list = {
        "password": None,
    }
    count_upper_letters = 0
    count_lower_letters = 0
    count_digits = 0
    password = params.get("password")
    if password is None:
        error_list["password"] = TYPES_OF_ERRORS["empty_passwd"]
    elif len(password) < 8:
        error_list["password"] = TYPES_OF_ERRORS["password_smallest_length"]
    elif len(password) > 128:
        error_list["password"] = TYPES_OF_ERRORS["password_biggest_length"]
    elif password.find(" ") > -1:
        error_list["password"] = TYPES_OF_ERRORS["password_with_spaces"]
    else:
        for char in password:
            if PERMITTED_CHARS_OF_PASSWORD.find(char.lower()) == -1:
                error_list["password"] = TYPES_OF_ERRORS["password_wrong_chars"]
                break
            elif char.isalpha():
                if char.isupper():
                    count_upper_letters += 1
                else:
                    count_lower_letters += 1
            elif char.isdigit():
                count_digits += 1
        if count_upper_letters < 1:
            error_list["password"] = TYPES_OF_ERRORS["password_not_upper_simbol"]
        elif count_lower_letters < 1:
            error_list["password"] = TYPES_OF_ERRORS["password_not_lower_simbol"]
        elif count_digits < 1:
            error_list["password"] = TYPES_OF_ERRORS["password_not_digit"]
    return error_list

def validation_create(params):
    PERMITTED_CHARS_OF_LOGIN = "abcdefghijklmnopqrstuvwxyz1234567890"
    PERMITTED_CHARS_OF_PASSWORD = '''abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890~!?@#$%^&*_-+()[]{}></\|"'.,:;'''
    error_list = {
        "login": None,
        "password": None,
        "last_name": None,
        "first_name": None,
        "error_check": 1,
    }
    login = params.get("login")
    if login is None:
        error_list["login"] = TYPES_OF_ERRORS["empty_login"]
        error_list["error_check"] = 0
    elif len(login) < 5:
        error_list["login"] = TYPES_OF_ERRORS["login_wrong_size"]
        error_list["error_check"] = 0
    else:
        for char in login:
             if PERMITTED_CHARS_OF_LOGIN.find(char.lower()) == -1:
                 error_list["login"] = TYPES_OF_ERRORS["login_wrong_chars"]
                 error_list["error_check"] = 0
                 break
             
    if params.get("last_name") is None:
        error_list["last_name"] = TYPES_OF_ERRORS["empty_last_name"]
        error_list["error_check"] = 0

    if params.get("first_name") is None:
        error_list["first_name"] = TYPES_OF_ERRORS["empty_first_name"]
        error_list["error_check"] = 0

    checked_password = check_password(params, PERMITTED_CHARS_OF_PASSWORD)
    if not checked_password.get("password") is None:
        error_list["password"] = checked_password["password"]
        error_list["error_check"] = 0

    return error_list

def params(names_list):
    result = {}
    for name in names_list:
        result[name] = request.form.get(name) or None
    return result

@app.route('/users/create', methods=['POST'])
@login_required
def create_user():
    cur_params = params(PERMITTED_PARAMS)

    errors = validation_create(cur_params)
    if errors["error_check"] == 0:
        flash("Проверьте правильность введённых данных", "danger")
        return render_template("users/new.html", roles = load_roles(), user=cur_params, errors=errors)

    inserted = insert_to_db(cur_params)
    if inserted:
        flash("Пользователь успешно добавлен", "success")
        return redirect(url_for("users"))
    else:
        flash("При сохранении возникла ошибка", "danger")
        return render_template("users/new.html", roles = load_roles(), user=cur_params, errors=errors)

@app.route('/users/<int:user_id>/edit', methods=['GET'])
@login_required
def edit_user(user_id):
    edit_select = "SELECT * FROM users WHERE id = %s;"
    errors = {}
    with db.connection.cursor(named_tuple = True) as cursor:
        cursor.execute(edit_select, (user_id,))
        user = cursor.fetchone()
        if user is None:
            flash("Пользователь не найден", "warning")
            return redirect(url_for("users"))
        
    return render_template("users/edit.html", user=user, roles=load_roles(), errors=errors)

@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required
def update_user(user_id):
    cur_params = params(PERMITTED_PARAMS)
    errors = validation_create(cur_params)
    cur_params["id"] = user_id
    update_query = """
    UPDATE users SET last_name = %(last_name)s, 
    first_name = %(first_name)s, middle_name = %(middle_name)s,
    role_id = %(role_id)s WHERE id = %(id)s;
    """
    if errors["error_check"] == 0:
        flash("Проверьте правильность введённых данных", "danger")
        return render_template('users/edit.html', user=cur_params, roles=load_roles(), errors=errors)

    try:
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(update_query, cur_params)
            db.connection.commit()
            flash("Пользователь успешно обновлен", "success")
    except mysql.connector.errors.DatabaseError:
        flash("При изменении возникла ошибка", "danger")
        db.connection.rollback()
        return render_template('users/edit.html', user=cur_params, roles=load_roles(), errors=errors)
        
    return redirect(url_for("users"))
    
    
@app.route("/users/<int:user_id>")
def show_user(user_id):
    with db.connection.cursor(named_tuple = True) as cursor:
        query="SELECT * FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        db_user = cursor.fetchone()
    if db_user is None:
        flash("Пользователь не найден", "danger")
        return redirect(url_for("users"))
    
    return render_template('users/show.html', user=db_user)

@app.route("/users/<int:user_id>/delete", methods=['POST'])
@login_required
def delete_user(user_id):
    delete_query="DELETE FROM users WHERE id = %s"
    try:
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(delete_query, (user_id,))
            db.connection.commit()
            flash("Пользователь успешно удален", "success")
    except mysql.connector.errors.DatabaseError:
        flash("При удалении произошла ошибка", "danger")
        db.connection.rollback()
    return redirect(url_for("users"))

@app.route("/update_password", methods=['GET', 'POST'])
@login_required
def update_password():
    user_id = current_user.id
    PERMITTED_PASSWORD = '''abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя1234567890~!?@#$%^&*_-+()[]{}></\|"'.,:;'''
    errors = {
        "old": None,
        "check": None,
        "password": None, 
        "error_check": 1,
    }
    fields = {
        "old": "",
        "new": "",
        "check": "",
    }
    if request.method == "POST":
        old_passwd = request.form.get("floatingOldPassword")
        new_passwd = request.form.get("floatingNewPassword")
        check_new_passwd = request.form.get("floatingCheckPassword")
        fields["old"] = old_passwd
        fields["new"] = new_passwd
        fields["check"] = check_new_passwd
        query = "SELECT * FROM users WHERE id = %s AND password_hash = SHA2(%s, 256);"
        with db.connection.cursor(named_tuple = True) as cursor:
            cursor.execute(query, (user_id, old_passwd))
            print(cursor.statement)
            db_user = cursor.fetchone()
            if db_user is None:
                errors["old"] = TYPES_OF_ERRORS["wrong_password"]
                errors["error_check"] = 0
            validate_password = check_password({"password": new_passwd}, PERMITTED_PASSWORD)
            if not validate_password.get("password") is None:
                errors["password"] = validate_password["password"]
                errors["check"] = validate_password["password"]
                errors["error_check"] = 0
            if new_passwd != check_new_passwd:
                errors["check"] = TYPES_OF_ERRORS["wrong_checked_password"]
                errors["error_check"] = 0
        if errors.get("error_check") == 0:
            flash("Проверьте введённые данные", "danger")
            return render_template('update_password.html', errors=errors, fields=fields)
    
        update_query = "UPDATE users SET password_hash = SHA2(%s, 256) WHERE id = %s;"
        try:
            with db.connection.cursor(named_tuple = True) as cursor:
                cursor.execute(update_query, (new_passwd, user_id))
                db.connection.commit()
                flash("Пароль успешно обновлен", "success")
                return redirect(url_for("index"))
        except mysql.connector.errors.DatabaseError:
            flash("При изменении возникла ошибка", "danger")
            db.connection.rollback()
            return render_template('update_password.html', errors=errors, fields=fields)
    return render_template('update_password.html', errors=errors, fields=fields)