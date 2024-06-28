import io

import pandas as pd
from flask import render_template, request, redirect, url_for, session, flash, send_file

from modules.db import get_db_connection, get_db_cursor


def create_export_routes(app):
    cursor = get_db_cursor()
    conn = get_db_connection()

    @app.route('/export', methods=['GET', 'POST'])
    def export():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            table_name = request.form.get('table_name')

            if not table_name or table_name not in session['allowed_tables']:
                flash('Неправильное имя таблицы', 'danger')
                return redirect(url_for('export'))

            return render_template('export/export_result.html', table_name=table_name, )

        return render_template('export/export.html')

    @app.route('/export/<format>/<table_name>')
    def export_file(format, table_name):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if format == 'xlsx':
            df = get_data_from_database(table_name)

            # Создайте XLSX файл из данных
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Sheet1', index=False)
            output.seek(0)

            # Отправьте файл пользователю
            return send_file(output, as_attachment=True, download_name=f'{table_name}.xlsx',
                             mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        elif format == 'csv':
            df = get_data_from_database(table_name)

            # Создайте CSV файл из данных
            output = io.BytesIO()
            df.to_csv(output, index=False, encoding='utf-8')
            output.seek(0)

            # Отправьте файл пользователю
            return send_file(output, as_attachment=True, download_name=f'{table_name}.csv', mimetype='text/csv')
        else:
            return redirect(url_for('index'))  # Перенаправление на главную страницу, если указан неверный формат

    # Функция для получения данных из базы данных (замените на свою логику)
    def get_data_from_database(table_name):
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        df = pd.DataFrame(data, columns=column_names)
        return df
