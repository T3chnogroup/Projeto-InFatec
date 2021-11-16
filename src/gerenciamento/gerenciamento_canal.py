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

#Função que insere participantes no canal
def adicionar_lista_emails(emails, id_canal, email_logado):
    for email in emails:
        if email != email_logado: #Se o email for diferente do email logado, será inserido como participante
            adicionar_email(email,id_canal) #adicona o email ao canal

 #adiciona participantes no canal depois que o canal foi criado
def adicionar_email(email, id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario from usuario where email = %s", (email,)) # busca o id do usuario com este email no banco
    if cur.rowcount > 0:# se existir esse id
        id_usuario = cur.fetchall()[0][0]
        cur.execute("INSERT IGNORE INTO canal_usuario(id_canal, id_usuario, funcao) VALUES (%s, %s, 'participante')", (id_canal, id_usuario)) #inserir na tabela canal_usuario como participante
    mysql.connection.commit()
    cur.close()

#Altera a função de participante para moderador e moderador para participante
def alterar_funcao_membro(id_usuario, id_canal, funcao):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE canal_usuario SET funcao = %s where id_canal = %s and id_usuario = %s", (funcao, id_canal, id_usuario,)) #inserir na tabela canal_usuario como participante
    mysql.connection.commit()
    cur.close()

#Remove membro do canal
def remover_membros(id_usuario, id_canal):
    cur = mysql.connection.cursor()
    cur.execute("DELETE from canal_usuario where id_canal = %s and id_usuario = %s", (id_canal, id_usuario,))
    mysql.connection.commit()
    cur.close()

#Exclui o canal
def excluir_canal(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("DELETE from canal_usuario where id_canal = %s", (id_canal,)) #Exclui todos os membros do canal
    cur.execute("DELETE from post where fk_canal = %s", (id_canal,)) #Exclui todos os posts do canal
    cur.execute("DELETE from canal where id_canal = %s", (id_canal,)) #Exclui todo o canal
    mysql.connection.commit()
    cur.close()

#Lista os canais no sidebar
def getcanais(id_usuario): 
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id_canal, nome, visibilidade FROM canal") # Seleciona a coluna id e a coluna nome do canal na tabela
    todos_canais_bd = cursor.fetchall()
    todos_canais = []
    for canal in todos_canais_bd:
        id_canal = canal[0]
        moderador = checagem_moderador(id_canal, id_usuario) #Verifica se é moderador do canal
        seguidor = segue_canal(id_canal, id_usuario) #Verifica se é seguidor do canal
        if canal[2] == 'privado':
            if not seguidor:
                continue
        nova_tupla = canal + (moderador, seguidor)
        todos_canais.append(nova_tupla)
    return todos_canais

#Checka se um usuário é moderador do canal
def checagem_moderador(id_canal,  id_usuario):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from canal_usuario where id_canal = %s and id_usuario = %s and funcao = 'moderador'",(id_canal, id_usuario))
    if cursor.rowcount > 0:
        return True
    else:
        return False

#Função que verifica se o usuário segue o canal
def segue_canal(id_canal, id_usuario): 
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from canal_usuario where id_canal = %s and id_usuario = %s",(id_canal, id_usuario))
    if cursor.rowcount > 0:
        return True
    else:
        return False

#Função que exclui o usuário do canal caso o mesmo clique no botão "Deixar de seguir canal"
def deixa_de_seguir(id_canal, id_usuario):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE from canal_usuario where id_canal = %s and id_usuario = %s", (id_canal, id_usuario))
    mysql.connection.commit()
    cursor.close()

#Função que insere usuário como participante no canal caso o mesmo clique no botão "Seguir canal"
def seguir(id_canal, id_usuario):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT IGNORE INTO canal_usuario(id_canal, id_usuario, funcao) VALUES (%s, %s, 'participante')", (id_canal, id_usuario))
    mysql.connection.commit()
    cursor.close()

#Gerenciamento da visibilidade do canal (Público / Privado)
def editar_visibilidade(id_canal, visibilidade_canal):
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE canal SET visibilidade = %s where id_canal = %s",(visibilidade_canal, id_canal))
    mysql.connection.commit()
    cursor.close()

def recuperar_visibilidade_canal(id_canal):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT visibilidade from canal where id_canal = %s", (id_canal,))
    visibilidade = cursor.fetchall()[0][0]
    cursor.close()
    return visibilidade

