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
            adicionar_email(email,id_canal) #adiciona o email ao canal

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
    cur.execute("DELETE from canal_curso where id_canal = %s", (id_canal,))#Exclui todos os cursos do canal
    cur.execute("DELETE from canal_grupo where id_canal = %s", (id_canal,))#Exclui todos os grupos do canal
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
        fixado = canal_fixado(id_canal, id_usuario) #Verifica se o canal é fixo
        if canal[2] == 'privado':
            if not fixado:
                continue
        nova_tupla = canal + (moderador, fixado)
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

#Função que verifica se o usuário fixou o canal
def canal_fixado(id_canal, id_usuario): 
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * from canal_usuario where id_canal = %s and id_usuario = %s",(id_canal, id_usuario))
    if cursor.rowcount > 0:
        return True
    else:
        return False

#Função que exclui o usuário do canal caso o mesmo clique no botão "Desafixar canal"
def desafixa_canal(id_canal, id_usuario):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE from canal_usuario where id_canal = %s and id_usuario = %s", (id_canal, id_usuario))
    mysql.connection.commit()
    cursor.close()

#Função que insere usuário como participante no canal caso o mesmo clique no botão "Fixar canal"
def fixar_canal(id_canal, id_usuario):
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

def criar_canal(nome, visibilidade, emails, grupos, cursos):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO canal(nome, visibilidade) VALUES (%s, %s)", (nome, visibilidade))
    cur.execute("SELECT max(id_canal) FROM canal where nome = %s", (nome,)) # Select utilizado por ter nomes de canal duplicado
    id_canal = cur.fetchall()[0]
    #Saber qual o id do usuário
    email_logado = request.cookies.get('email_logado')
    adicionar_lista_emails(emails, id_canal, email_logado)
    cur.execute("SELECT id_usuario from usuario where email = %s", (email_logado,)) # busca o id do usuario com este email no banco
    if cur.rowcount > 0:# se existir esse id
        id_usuario = cur.fetchall()[0][0]
        cur.execute("INSERT INTO canal_usuario(id_canal, id_usuario, funcao) VALUES (%s, %s, 'moderador')", (id_canal, id_usuario)) #inserir na tabela canal_usuario como moderador
    mysql.connection.commit()   
    cur.close()
    adicionar_lista_grupos(id_canal, grupos)
    adicionar_lista_cursos(id_canal, cursos)
    return id_canal

def adicionar_lista_grupos(id_canal, grupos):
    for grupo in grupos:
        adicionar_grupo(id_canal, grupo)

def adicionar_grupo(id_canal, id_grupo):
    cur = mysql.connection.cursor()
    cur.execute("INSERT IGNORE INTO canal_grupo (id_canal, id_grupo) VALUES (%s, %s)", (id_canal, id_grupo))
    mysql.connection.commit()
    cur.close()

def adicionar_lista_cursos(id_canal, cursos):
    for curso in cursos:
        adicionar_curso(id_canal, curso)

def adicionar_curso(id_canal, nome_curso):
    cur = mysql.connection.cursor()
    cur.execute("INSERT IGNORE INTO canal_curso (id_canal, nome_curso) VALUES (%s, %s)", (id_canal, nome_curso))
    mysql.connection.commit()
    cur.close()

def retorna_grupos(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_grupo from canal_grupo where id_canal = %s", (id_canal,))
    grupos = cur.fetchall()
    cur.close()
    grupos_str = ''
    tamanho_grupos = len(grupos)
    for indice, grupo in enumerate(grupos): #Para cada indice da tupla na enumeração de tuplas, 
        if grupo[0] == 1:                   #se a primeira coluna da tupla for igual a 1 é concatenado a string vazia da variável grupos_str com 'Coordenadores'
            grupos_str += 'Coordenadores'   #assim sucessivamente para os valaores 2 e 3
        if grupo[0] == 2:
            grupos_str += 'Professores'
        if grupo[0] == 3:
            grupos_str += 'Alunos'
        if indice < tamanho_grupos - 1: #Se não for o ultimo elemento da lsta de tuplas adiciona ',' e espaço.
            grupos_str += ', '
    return grupos_str

def retorna_cursos(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT nome_curso from canal_curso where id_canal = %s", (id_canal,))
    cursos =  cur.fetchall()
    cur.close()
    cursos_str = ''
    tamanho_cursos = len(cursos)
    for indice, curso in enumerate(cursos):
        cursos_str = cursos_str + curso[0]
        if indice < tamanho_cursos - 1:
            cursos_str = cursos_str + ', '
    return cursos_str

#Função que retorna se Coordenadores estão selecionados no canal
def coordenadores_selecionados(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from canal_grupo where id_grupo = 1 and id_canal = %s", (id_canal,))
    if cur.rowcount > 0:
        existe = True
    else:
        existe = False
    cur.close()
    return existe

#Função que retorna se Professores estão selecionados no canal
def professores_selecionados(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from canal_grupo where id_grupo = 2 and id_canal = %s", (id_canal,))
    if cur.rowcount > 0:
        existe = True
    else:
        existe = False
    cur.close()
    return existe

#Função que retorna se Alunos estão selecionados no canal
def alunos_selecionados(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * from canal_grupo where id_grupo = 3 and id_canal = %s", (id_canal,))
    if cur.rowcount > 0:
        existe = True
    else:
        existe = False
    cur.close()
    return existe

#Função que retorna a lista de cursos que estão selecionados no canal
def lista_cursos(id_canal):
    cur = mysql.connection.cursor()
    cur.execute("SELECT nome_curso from canal_curso where id_canal = %s", (id_canal,))
    tuplas =  cur.fetchall()
    cur.close()
    lista = []
    for linha in tuplas:
        lista.append(linha[0])
    return lista