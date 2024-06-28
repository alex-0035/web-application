from flask import render_template, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired

from config import app_config
from helpers.decorators import login_required
from modules.db import get_db_connection, get_db_cursor


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


def create_auth_routes(app):
    cursor = get_db_cursor()
    conn = get_db_connection()

    def initialize_user_session(user):
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['role'] = user[3]
        session['preferred_lang'] = user[4]

        lang_mapping = app_config.dynamic_menus[1]['mapping'][user[4]]
        # Load translations
        cursor.execute(f'SELECT translation_key, translation_{lang_mapping} FROM translations')
        translations = cursor.fetchall()
        session['translations'] = {key: value for key, value in translations}

        # Получаем список разрешенных таблиц для роли пользователя
        cursor.execute("SELECT * FROM user_roles WHERE role_type=?", (user[3],))

        # example: (2, 'user', 'Договора, Начисления, Оплаты', 1, 1, 1, 1)
        user_data = cursor.fetchone()

        # Сохраняем список разрешенных таблиц в сессии
        session['allowed_tables'] = user_data[2].replace(' ', '').split(',') if user_data else []
        session['allowed_search'] = user_data[3]
        session['allowed_add'] = user_data[4]
        session['allowed_delete'] = user_data[5]
        session['allowed_edit'] = user_data[6]

    def authenticate(username, password):
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        return cursor.fetchone()

    @app.route('/', methods=['GET', 'POST'])
    def start():
        if app_config.show_org_data:
            render_template('index.html', no_login=True)
        else:
            form = LoginForm()
            return render_template('auth/login.html', form=form)
        return render_template('index.html', no_login=True)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = authenticate(form.username.data, form.password.data)
            if user:
                initialize_user_session(user)
                flash('Вы успешно вошли!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Неправильное имя пользователя или пароль', 'danger')

        return render_template('auth/login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # Проверка, что пользователь с таким именем не существует
            cursor.execute("SELECT * FROM users WHERE username=?", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('Пользователь с таким именем уже существует!', 'error')
            else:
                cursor.execute("INSERT INTO users (username, password, role_type) VALUES (?, ?)",
                               (username, password, "user"))
                conn.commit()
                flash('Вы успешно зарегистрировались!', 'success')

                cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
                user = cursor.fetchone()
                session['username'] = user[1]
                session['user_id'] = user[0]
                flash('Вы успешно вошли!', 'success')
                return redirect(url_for('index'))

        return render_template('auth/register.html', form=form)

    @app.route('/change_password', methods=['GET', 'POST'])
    @login_required(message='[AUTH] Please log in to change your password.')
    def change_password():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            new_password = request.form['new_password']

            # Update the user's password in the database
            user_id = session['user_id']
            cursor.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
            conn.commit()

            flash('Password changed successfully', 'success')
            return redirect(url_for('index'))

        return render_template('auth/change_password.html')

    # Роут для выхода
    @app.route('/logout')
    @login_required(message='[AUTH] Please log in to log out.')
    def logout():
        session.clear()
        flash('Вы успешно вышли из системы', 'success')
        return render_template('index.html', no_login=True, )
