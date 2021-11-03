import os
import re
from MySQLdb.cursors import Cursor
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv
load_dotenv(".env")

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_Host'] = os.getenv("MYSQL_Host")
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)

#Função que lista os usuarios
def listar_usuario():
    cursor = mysql.connection.cursor()
    cursor.execute('Select usuario.id_usuario, nome, email from usuario order by nome')
    Usuarios = cursor.fetchall()
    return Usuarios