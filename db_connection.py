"""Kết nối SQL Server bằng Windows Authentication."""
import os
import re

import pyodbc

SERVER = os.getenv("COFFEE_SQL_SERVER", r"THINKPADX1\SQLSEVER")
DATABASE = os.getenv("COFFEE_SQL_DATABASE", "QuanLyQuanCoffee")


def database_name():
    # Tên database không dùng được placeholder nên chỉ nhận tên an toàn.
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,127}", DATABASE):
        raise ValueError("Tên cơ sở dữ liệu không hợp lệ.")
    return DATABASE


def connect(database=None, autocommit=False):
    installed = pyodbc.drivers()
    driver = None
    for name in ("ODBC Driver 17 for SQL Server", "SQL Server"):
        if name in installed:
            driver = name
            break
    if not driver:
        raise RuntimeError("Không tìm thấy ODBC Driver 17 for SQL Server hoặc SQL Server.")
    target = database or database_name()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,127}", target):
        raise ValueError("Tên cơ sở dữ liệu không hợp lệ.")
    connection = pyodbc.connect(
        f"DRIVER={{{driver}}};SERVER={SERVER};DATABASE={target};"
        "Trusted_Connection=yes;", timeout=8, autocommit=autocommit,
    )
    connection.timeout = 15
    return connection


def rows(cursor):
    columns = []
    for column in cursor.description:
        columns.append(column[0])
    result = []
    for row in cursor.fetchall():
        item = {}
        for index in range(len(columns)):
            item[columns[index]] = row[index]
        result.append(item)
    return result
