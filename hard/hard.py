#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import psycopg2


"""
Необходимо доработать предыдущее задание, самостоятельно изучить работу с пакетом 
python-psycopg2 для работы с базами данных PostgreSQL. Для своего варианта лабораторной 
работы 2.17 необходимо реализовать возможность хранения данных в базе данных СУБД 
PostgreSQL. Информация в базе данных должна храниться не менее чем в двух таблицах.

Необходимо использовать словарь, содержащий следующие ключи: название пункта назначения; 
номер поезда; время отправления. Написать программу, выполняющую следующие действия: ввод 
с клавиатуры данных в список, состоящий из словарей заданной структуры; записи должны быть 
упорядочены по времени отправления поезда; вывод на экран информации о поездах, направляющихся 
в пункт, название которого введено с клавиатуры; если таких поездов нет, выдать на дисплей 
соответствующее сообщение (Вариант 26 (7), работа 2.8).
"""


def connect_db():
    """
    Установить соединение с базой данных PostgreSQL.
    """
    conn = psycopg2.connect(
        dbname="trains_db",
        user="postgres",
        password="1522",
        host="localhost",
        port=5432
    )
    return conn


def create_tables():
    """
    Создать таблицы в базе данных.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stations (
        station_id SERIAL PRIMARY KEY,
        station_name TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trains (
        train_id SERIAL PRIMARY KEY,
        departure_point INTEGER NOT NULL,
        number_train TEXT NOT NULL,
        time_departure TEXT NOT NULL,
        destination INTEGER NOT NULL,
        FOREIGN KEY (departure_point) REFERENCES stations (station_id),
        FOREIGN KEY (destination) REFERENCES stations (station_id)
        )
        """
    )

    conn.commit()
    conn.close()


def add_train(name_dep, number_train, time_departure, name_dest):
    """
    Добавить данные о поезде.
    """
    conn = connect_db()
    cursor = conn.cursor()

    # Получить или добавить станцию отправления.
    cursor.execute(
        "SELECT station_id FROM stations WHERE station_name = %s",
        (name_dep,)
    )
    dep_row = cursor.fetchone()
    if dep_row is None:
        cursor.execute(
            "INSERT INTO stations (station_name) VALUES (%s) RETURNING station_id",
            (name_dep,)
        )
        dep_id = cursor.fetchone()[0]
    else:
        dep_id = dep_row[0]

    # Получить или добавить станцию назначения.
    cursor.execute(
        "SELECT station_id FROM stations WHERE station_name = %s",
        (name_dest,)
    )
    dest_row = cursor.fetchone()
    if dest_row is None:
        cursor.execute(
            "INSERT INTO stations (station_name) VALUES (%s) RETURNING station_id",
            (name_dest,)
        )
        dest_id = cursor.fetchone()[0]
    else:
        dest_id = dest_row[0]

    # Добавить поезд.
    cursor.execute(
        """
        INSERT INTO trains (departure_point, number_train, time_departure, destination)
        VALUES (%s, %s, %s, %s)
        """,
        (dep_id,
         number_train,
         time_departure,
         dest_id)
    )

    conn.commit()
    conn.close()


def display_trains():
    """
    Отобразить список поездов со станциями.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT t.train_id, s1.station_name AS departure, t.number_train, t.time_departure, 
        s2.station_name AS destination
        FROM trains t
        JOIN stations s1 ON t.departure_point = s1.station_id
        JOIN stations s2 ON t.destination = s2.station_id
        """
    )

    rows = cursor.fetchall()
    conn.close()

    if rows:
        line = '+-{}-+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 13,
            '-' * 18,
            '-' * 30)
        print(line)

        print('| {:^4} | {:^30} | {:^13} | {:^18} | {:^30} |'.format(
            "№",
            "Пункт отправления",
            "Номер поезда",
            "Время отправления",
            "Пункт назначения")
        )
        print(line)

        for row in rows:
            print('| {:>4} | {:<30} | {:<13} | {:>18} | {:<30} |'.format(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4]))
            print(line)

    else:
        print("Список поездов пуст.")


def select_trains(point_user):
    """
    Выбрать поезда по пункту назначения.
    """
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT t.train_id, s1.station_name AS departure, t.number_train, 
        t.time_departure, s2.station_name AS destination
        FROM trains t
        JOIN stations s1 ON t.departure_point = s1.station_id
        JOIN stations s2 ON t.destination = s2.station_id
        WHERE LOWER(s2.station_name) = %s
        """,
        (point_user.lower(),)
    )

    rows = cursor.fetchall()
    conn.close()

    if rows:
        line = '+-{}-+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 13,
            '-' * 18,
            '-' * 30)
        print(line)

        print('| {:^4} | {:^30} | {:^13} | {:^18} | {:^30} |'.format(
            "№",
            "Пункт отправления",
            "Номер поезда",
            "Время отправления",
            "Пункт назначения")
        )
        print(line)

        for row in rows:
            print('| {:>4} | {:<30} | {:<13} | {:>18} | {:<30} |'.format(
                row[0],
                row[1],
                row[2],
                row[3],
                row[4]))
            print(line)

    else:
        print("Список поездов пуст.")


def main(command_line=None):
    parser = argparse.ArgumentParser("trains")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    add = subparsers.add_parser(
        "add",
        help="Add a new train"
    )
    add.add_argument(
        "-dep",
        "--departure_point",
        action="store",
        required=True,
        help="The train's departure point"
    )
    add.add_argument(
        "-n",
        "--number_train",
        action="store",
        required=True,
        help="The train's number"
    )
    add.add_argument(
        "-t",
        "--time_departure",
        action="store",
        required=True,
        help="The time departure of train"
    )
    add.add_argument(
        "-des",
        "--destination",
        action="store",
        required=True,
        help="The destination of train"
    )

    _ = subparsers.add_parser(
        "display",
        help="Display all trains"
    )

    select = subparsers.add_parser(
        "select",
        help="Select the trains"
    )
    select.add_argument(
        "-P",
        "--point_user",
        action="store",
        required=True,
        help="The required point"
    )

    args = parser.parse_args(command_line)

    create_tables()

    if args.command == "add":
        add_train(
            args.departure_point,
            args.number_train,
            args.time_departure,
            args.destination
        )
    elif args.command == "display":
        display_trains()
    elif args.command == "select":
        select_trains(args.point_user)


if __name__ == "__main__":
    main()
