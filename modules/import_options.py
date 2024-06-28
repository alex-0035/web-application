import csv

import pandas as pd
from flask import render_template, request, redirect, url_for, session, flash, send_file
import io
from modules.db import get_db_connection, get_db_cursor


def create_import_routes(app):
    cursor = get_db_cursor()
    conn = get_db_connection()

    @app.route('/add/<table_name>/csv', methods=['POST'])
    def add_csv_to_table(table_name):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        try:
            if 'csvFile' in request.files:
                csv_file = request.files['csvFile']
                if csv_file.filename != '':
                    # Read the CSV file
                    csv_text = io.TextIOWrapper(csv_file, encoding='utf-8')
                    csv_reader = csv.reader(csv_text)

                    # Get column names from the first row
                    header = next(csv_reader)

                    # Iterate through CSV rows and insert them into the table
                    for row in csv_reader:
                        placeholders = ','.join(['?'] * len(row))
                        cursor.execute(f"INSERT INTO {table_name} ({', '.join(header)}) VALUES ({placeholders})", row)
                        conn.commit()

                    flash('Data from CSV file successfully added', 'success')
                else:
                    flash('No file selected for upload', 'danger')
            else:
                flash('No file field in the form', 'danger')
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

        return redirect(url_for('manage_table', table_name=table_name))
