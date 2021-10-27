import os
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

#Função que dado um canal lista os membros moderadores dele
def listar_moderador(id_canal):
    cursor = mysql.connection.cursor()
    cursor.execute('Select usuario.id_usuario, nome, email, funcao from canal_usuario join usuario on (canal_usuario.id_usuario = usuario.id_usuario) where id_canal = %s and funcao = \'moderador\' order by nome', (id_canal,)) #Seleciona os dados da tabela usuario e junta com a tabela canal_usuário e compara os id_usuario e ordena por ordem alfabética (nome)
    Membros = cursor.fetchall()
    return Membros

#Função que dado um canal lista os membros participantes dele
def listar_participante(id_canal):
    cursor = mysql.connection.cursor()
    cursor.execute('Select usuario.id_usuario, nome, email, funcao from canal_usuario join usuario on (canal_usuario.id_usuario = usuario.id_usuario) where id_canal = %s and funcao = \'participante\' order by nome', (id_canal,)) #Seleciona os dados da tabela usuario e junta com a tabela canal_usuário e compara os id_usuario e ordena por ordem alfabética (nome)
    Membros = cursor.fetchall()
    return Membros
