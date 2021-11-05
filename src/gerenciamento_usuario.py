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
    cur = mysql.connection.cursor()
    cur.execute('Select usuario.id_usuario, nome, email, pode_gerenciar_usuario, pode_criar_canais from usuario order by nome')
    Usuarios = cur.fetchall()
    return Usuarios

#Remove usuário da aplicação
def remover_usuario(id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("DELETE from post where fk_usuario = %s", (id_usuario,)) #Exclui todos os posts do canal
    cur.execute("DELETE from canal_usuario where id_usuario = %s", (id_usuario,)) #Exclui usuário dos canais
    cur.execute("DELETE from usuario where id_usuario = %s", (id_usuario,)) #Exclui usuario da aplicação
    mysql.connection.commit()
    cur.close()

#Edita as permissões do usuário
def editar_permissoes(id_usuario, pode_gerenciar_usuario, pode_criar_canais):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuario SET pode_gerenciar_usuario = %s, pode_criar_canais = %s where id_usuario = %s", (pode_gerenciar_usuario,pode_criar_canais, id_usuario,)) 
    mysql.connection.commit()
    cur.close()

def pode_criar_canais(id_usuario):
    cur= mysql.connection.cursor()
    #Esse usuario pode criar canal?
    cur.execute('Select id_usuario, pode_criar_canais from usuario where id_usuario = %s', (id_usuario,))
    pode_criar_canais = cur.fetchall()[0][0]
    if pode_criar_canais == 1:
        return True
    else:
        return False

def pode_gerenciar_usuarios(id_usuario):
    cur= mysql.connection.cursor()
    #Esse usuario pode gerenciar usuario?
    cur.execute('Select id_usuario, pode_gerenciar_usuario from usuario where id_usuario = %s', (id_usuario,))
    pode_criar_canais = cur.fetchall()[0][1]
    if pode_criar_canais == 1:
        return True
    else:
        return False