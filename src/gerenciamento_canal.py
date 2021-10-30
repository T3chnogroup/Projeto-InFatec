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

def adicionar_lista_emails(emails, id_canal, email_logado):
    for email in emails:
        if email != email_logado: #Se o email for diferente do email logado, será inserido como participante
            print(f'Adicionando o  email {email} ao  canal {id_canal}')
            adicionar_email(email,id_canal) #adicona o email ao canal

def adicionar_email(email, id_canal): #adiciona membro no canal depois que o canal foi criado
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario from usuario where email = %s", (email,)) # busca o id do usuario com este email no banco
    if cur.rowcount > 0:# se existir esse id
        id_usuario = cur.fetchall()[0][0]
        print(f'Adicionando o usuario {id_usuario} ao canal {id_canal}')
        cur.execute("INSERT IGNORE INTO canal_usuario(id_canal, id_usuario, funcao) VALUES (%s, %s, 'participante')", (id_canal, id_usuario)) #inserir na tabela canal_usuario como participante
    mysql.connection.commit()
    cur.close()

def alterar_funcao_membro(id_usuario, id_canal, funcao):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE canal_usuario SET funcao = %s where id_canal = %s and id_usuario = %s", (funcao, id_canal, id_usuario,)) #inserir na tabela canal_usuario como participante
    mysql.connection.commit()
    cur.close()

def remover_membros(id_usuario, id_canal):
    cur = mysql.connection.cursor()
    cur.execute("DELETE from canal_usuario where id_canal = %s and id_usuario = %s", (id_canal, id_usuario,))
    mysql.connection.commit()
    cur.close()

def excluir_canal(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("DELETE from canal_usuario where id_canal = %s", (id_canal,)) #Exclui todos os membros do canal
    cur.execute("DELETE from post where fk_canal = %s", (id_canal,)) #Exclui todos os posts do canal
    cur.execute("DELETE from canal where id_canal = %s", (id_canal,)) #Exclui todo o canal
    mysql.connection.commit()
    cur.close()