import os

import pymysql
from pymysql.cursors import DictCursor

#cria uma conexão com o banco
def get_db_connection():

    #abre a conexão usando as configurações do .env
    connection = pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False
    )

    #cria o cursor que executa os comandos sql
    cursor = connection.cursor()

    #retorna a conexão e cursor
    return connection, cursor