# config.py

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class AppConfig:
    db_path: str
    secret_key: str
    org_name: str
    show_org_data: bool = True                  # True = start page with org data + login, False = login
    page_size: int = 10                         # Number of records per page (pagination)
    log_to_file: bool = False                   # True = log to file, False = log to console
    # use_redis: bool = False                     # True = use Redis
    default_lang: str = 'en'
    static_menus: List[Dict[str, str]] = None   # List of static menus
    dynamic_menus: List[Dict] = None            # List of dynamic menus
    routes: List[Dict] = None                   # List of routes


app_config = AppConfig(
    db_path='db.sqlite',
    secret_key='secret',
    org_name='Example LLC @ 2023',
    show_org_data=False,
    page_size=10,
    default_lang='en',
    static_menus=[
        {
            "name": "export",
            "href": "/export"
        },
        {
            "name": "statistics",
            "href": "/statistics"
        },
        {
            "name": "about",
            "href": "/about"
        }
    ],
    dynamic_menus=[
        {
            "name": "data_management",
            "id": "manageDropdown",
            "href": "/table/",
            "dropdown_elements": "allowed_tables",
        },
        {
            "name": "lang",
            "id": "languageDropdown",
            "href": "/language/",
            "dropdown_elements": ["Русский", "English"],
            "mapping": {"Русский": "ru", "English": "en"},
        }
    ],
    routes=[
        {
            "route_name": '/language/<lang_name>',
            "callname": "change_language",
            "methods": ['GET'],
            "description": 'Change language route',
            "function": 'change_language(lang_name)'
        },
        {
            "route_name": '/index',
            "callname": "index",
            "methods": ['GET'],
            "description": 'Index route',
            "function": 'index()'
        },
        {
            "route_name": '/about',
            "callname": "about",
            "methods": ['GET'],
            "description": 'About route',
            "function": 'about()'
        },
        {
            "route_name": '/statistics',
            "callname": "statistics",
            "methods": ['GET'],
            "description": 'Statistics route',
            "function": 'statistics()'
        },
        {
            "route_name": '/',
            "callname": "login",
            "methods": ['GET', 'POST'],
            "description": 'Login route',
            "function": 'login()'
        },
        {
            "route_name": '/register',
            "callname": "register",
            "methods": ['GET', 'POST'],
            "description": 'Register route',
            "function": 'register()'
        },
        {
            "route_name": '/change_password',
            "callname": "change_password",
            "methods": ['GET', 'POST'],
            "description": 'Change password route',
            "function": 'change_password()'
        },
        {
            "route_name": '/logout',
            "callname": "logout",
            "methods": ['GET'],
            "description": 'Logout route',
            "function": 'logout()'
        },
        {
            "route_name": '/export',
            "callname": "export",
            "methods": ['GET', 'POST'],
            "description": 'Export options route',
            "function": 'export()'
        },
        {
            "route_name": '/export/<format>/<table_name>',
            "callname": "export_file",
            "methods": ['GET'],
            "description": 'Export file route',
            "function": 'export_file(format, table_name)'
        },
        {
            "route_name": '/add/<table_name>/csv',
            "callname": "add_csv_to_table",
            "methods": ['POST'],
            "description": 'Add CSV to table route',
            "function": 'add_csv_to_table(table_name)'
        },
        {
            "route_name": '/add/<table_name>',
            "callname": "add_record",
            "methods": ['GET', 'POST'],
            "description": 'Add record to table route',
            "function": 'add_record(table_name)'
        },
        {
            "route_name": '/edit/<table_name>/<int:record_id>',
            "callname": "edit_record",
            "methods": ['GET', 'POST'],
            "description": 'Edit record in table route',
            "function": 'edit_record(table_name, record_id)'
        },
        {
            "route_name": '/delete/<table_name>/<int:record_id>',
            "callname": "delete_record",
            "methods": ['GET', 'POST'],
            "description": 'Delete record in table route',
            "function": 'delete_record(table_name, record_id)'
        },
        {
            "route_name": '/table/<table_name>',
            "callname": "manage_table",
            "methods": ['GET'],
            "description": 'Manage table route',
            "function": 'manage_table(table_name)'
        },
    ]
)
