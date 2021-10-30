import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv
load_dotenv(".env")

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_Host'] = os.getenv("MYSQL_Host")
#app.config['MYSQL_HOST'] = '0.0.0.0'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
#app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)


def edit_post(id_post,conteudo):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE post SET conteudo=%s WHERE id_post=%s", (conteudo,id_post))
    mysql.connection.commit()
    cur.close()



    