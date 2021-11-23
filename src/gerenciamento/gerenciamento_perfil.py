import os
import re
from MySQLdb.cursors import Cursor
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv
load_dotenv(".env")

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)

def busca_user_id(id_usuario):
    cur = mysql.connection.cursor()
    cur.execute('select id_usuario, nome, email, cpf, senha from usuario where id_usuario = %s',str(id_usuario))
    usuario_logado = cur.fetchall()
    cur.close()
    return usuario_logado[0]

def editando_usuario(nome, email, cpf, id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE usuario
        SET nome=%s, email=%s, cpf=%s
        WHERE id_usuario = %s
    """, (nome, email, cpf, id_usuario))
    mysql.connection.commit()
    cur.close()
    

