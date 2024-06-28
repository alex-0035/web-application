import logging

import pandas as pd
import ydata_profiling
from flask import Flask, render_template, request, redirect, url_for, session, flash
# from celery import Celery

import modules.db
from config import app_config
from helpers.decorators import login_required
from modules.auth import create_auth_routes
from modules.export_options import create_export_routes
from modules.import_options import create_import_routes
from modules.tables import create_table_routes

app = Flask(__name__)
app.secret_key = app_config.secret_key

# Celery configuration
# if app_config.use_redis:
#     def make_celery(app):
#         celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
#         celery.conf.update(app.config)
#         TaskBase = celery.Task
#
#         class ContextTask(TaskBase):
#             abstract = True
#
#             def __call__(self, *args, **kwargs):
#                 with app.app_context():
#                     return TaskBase.__call__(self, *args, **kwargs)
#
#         celery.Task = ContextTask
#         return celery
#     app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
#     app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
#
#     # Initialize Celery
#     celery = make_celery(app)

# Register the authentication routes
create_auth_routes(app)

# Register the export routes
create_export_routes(app)

# Register the table routes
create_table_routes(app)

# Register the import options
create_import_routes(app)

# Подключение к базе данных SQLite
conn = modules.db.get_db_connection()
cursor = modules.db.get_db_cursor()

# Configure logging
if app_config.log_to_file:
    logging.basicConfig(filename="app.log", level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
else:
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

logger = logging.getLogger(__name__)


@app.context_processor
def inject_user():
    # Load translations
    if not session.get('translations'):
        cursor.execute(f'SELECT translation_key, translation_{app_config.default_lang} FROM translations')
        translations = cursor.fetchall()
        session['translations'] = {key: value for key, value in translations}

    session_variables = {
        'username': session.get('username'),
        'allowed_tables': session.get('allowed_tables', default=[]),
        'app_config': app_config,
        'org_name': session.get('org_name', default=app_config.org_name)
    }

    session_variables['user_data'] = {session['translations']['role']: session.get('role'),
                                      session['translations']['user_id']: session.get('user_id'),
                                      session['translations']['preferred_lang']: session.get('preferred_lang')}

    return session_variables


@app.errorhandler(404)
def page_not_found(e):
    logger.info(f'Page not found: {request.url}')
    request_url = request.url
    return render_template('error_page.html', error=e, request_url=request_url), 404


@app.route('/language/<lang_name>')
@login_required(message="Language change is available only for authorized users")
def change_language(lang_name):
    # Validate language choice
    if lang_name not in app_config.dynamic_menus[1]['mapping'].keys():
        return "Language not supported", 404

    try:
        lang_mapping = app_config.dynamic_menus[1]['mapping'][lang_name]
        # Load translations
        cursor.execute(f'SELECT translation_key, translation_{lang_mapping} FROM translations')
        translations = cursor.fetchall()
        session['translations'] = {key: value for key, value in translations}

        # Update user's preferred language
        if 'user_id' in session:
            session['preferred_lang'] = lang_name
            cursor.execute('UPDATE users SET preferred_lang = ? WHERE id = ?', (lang_name, session['user_id']))
            conn.commit()

    except Exception as e:
        conn.rollback()
        return f"An error occurred: {e}", 404

    return redirect(url_for('index'))


# example for celery task
# @celery.task
# def save_feedback(user_id, feedback):
#     # Logic to save feedback
#     cursor.execute('''INSERT INTO feedback (user_id, content) VALUES (?, ?)''', (user_id, feedback,))
#     conn.commit()

@app.route('/submit_feedback', methods=['POST'])
@login_required(message="Feedback is available only for authorized users")
def submit_feedback():
    feedback = request.form['feedback']
    user_id = session['user_id']
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, user_id integer, content TEXT)''')

    # with celery task: save_feedback.delay(user_id, feedback)
    cursor.execute('''INSERT INTO feedback (user_id, content) VALUES (?, ?)''', (user_id, feedback,))
    conn.commit()
    return redirect(url_for('index'))  # Redirect to the homepage or a 'thank you' page


# Роут для индексной страницы (после успешного входа)
@app.route('/index')
@login_required(message="Cabinet is available only for authorized users")
def index():
    return render_template('cabinet.html', )


# Роут для страницы "О нас"
@app.route('/about')
@login_required(message="About page is available only for authorized users")
def about():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('about.html')


# Роут для страницы "Статистика"
@app.route('/statistics')
@login_required(message="Statistics page is available only for authorized users")
def statistics():
    # Список таблиц, которые могут быть объединены
    tables_to_merge = []

    # Получаем данные из разрешенных таблиц
    for table_name in session['allowed_tables']:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        tables_to_merge.append(df)

    # Объединяем таблицы в один датафрейм
    merged_df = pd.concat(tables_to_merge, axis=0, ignore_index=True)

    # Создаем статистический отчет с помощью pandas-profiling
    profile = ydata_profiling.ProfileReport(merged_df)

    # Сохраните отчет в HTML-файл
    stat_report_url = "static/stats_report.html"
    profile.to_file(stat_report_url)

    return render_template('statistics.html',
                           report_url=stat_report_url, )


if __name__ == '__main__':
    app.run(debug=True)
