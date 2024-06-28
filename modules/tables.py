import pandas as pd
from flask import render_template, request, redirect, url_for, session, flash, send_file
import io

from flask_paginate import Pagination, get_page_parameter

from config import app_config
from modules.db import get_db_connection, get_db_cursor


def create_table_routes(app):
    cursor = get_db_cursor()
    conn = get_db_connection()

    # Роут для добавления записи в таблицу
    @app.route('/add/<table_name>', methods=['GET', 'POST'])
    def add_record(table_name):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            # Получите данные из формы и добавьте запись в таблицу
            data = [request.form.get(f'column_{i}') for i in range(len(request.form) + 1)]  # начните с индекса 1
            placeholders = ','.join(['?'] * len(data))
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", data)
            conn.commit()
            flash('Запись успешно добавлена', 'success')
            return redirect(url_for('manage_table', table_name=table_name))

        cursor.execute(f"PRAGMA table_info({table_name})")
        column_info = cursor.fetchall()
        column_names = [info[1] for info in column_info]

        return render_template('records/add_record.html', table_name=table_name, column_names=column_names[1:],
                               )

    # Роут для редактирования записи в таблице
    @app.route('/edit/<table_name>/<int:record_id>', methods=['GET', 'POST'])
    def edit_record(table_name, record_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            # Получите данные из формы и обновите запись в таблице
            data = [request.form.get(f'column_{i}') for i in range(len(request.form) + 1)][1:]  # начните с индекса 1
            placeholders = ','.join(
                [f"{column[1]} = ?" for column in cursor.execute(f"PRAGMA table_info({table_name})").fetchall() if
                 column != 'id'])

            cursor.execute(f"UPDATE {table_name} SET {placeholders} WHERE id=?", data + [record_id])
            conn.commit()
            flash('Запись успешно изменена', 'success')
            return redirect(url_for('manage_table', table_name=table_name))

        cursor.execute(f"SELECT * FROM {table_name} WHERE id=?", (record_id,))
        row = cursor.fetchone()
        if row:
            column_info = cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
            column_names = [info[1] for info in column_info]
            return render_template('records/edit_record.html', table_name=table_name, record_id=record_id,
                                   column_names=column_names, row=row)
        else:
            flash('Запись не найдена', 'danger')
            return redirect(url_for('manage_table', table_name=table_name))

    # Роут для удаления записи из таблицы
    @app.route('/delete/<table_name>/<int:record_id>', methods=['GET', 'POST'])
    def delete_record(table_name, record_id):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if request.method == 'POST':
            cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (record_id,))
            conn.commit()
            flash('Запись успешно удалена', 'success')
            return redirect(url_for('manage_table', table_name=table_name))

        cursor.execute(f"SELECT * FROM {table_name} WHERE id=?", (record_id,))
        row = cursor.fetchone()
        if row:
            return render_template('records/delete_record.html', table_name=table_name, record_id=record_id, row=row,
                                   allowed_tables=session['allowed_tables'])
        else:
            flash('Запись не найдена', 'danger')
            return redirect(url_for('manage_table', table_name=table_name))

    # Роут для управления таблицей
    @app.route('/table/<table_name>')
    def manage_table(table_name):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        if table_name not in session['allowed_tables']:
            flash('Доступ к данной таблице запрещен', 'danger')
            return redirect(url_for('index'))

        # Pagination parameters
        page = request.args.get(get_page_parameter(), type=int, default=1)
        per_page = app_config.page_size

        '''
            Если надо по юзерам 
            user_id = session.get('user_id')
            cursor.execute(f"SELECT * FROM {table_name} WHERE user_id=?", (user_id,))
            '''
        cursor.execute(f"SELECT * FROM {table_name}")

        table_data = cursor.fetchall()

        # Search functionality
        search_query = request.args.get('q', '')
        if search_query:
            table_data = [row for row in table_data if
                          any(str(search_query).lower() in str(value).lower() for value in row)]

        column_names = [description[0] for description in cursor.description]

        # Calculate pagination parameters
        total = len(table_data)
        offset = (page - 1) * per_page
        end = offset + per_page

        # Apply pagination to the data
        table_data = table_data[offset:end]

        pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

        return render_template('table.html', table_name=table_name,
                               table_data=table_data, column_names=column_names,
                               pagination=pagination, search_query=search_query)