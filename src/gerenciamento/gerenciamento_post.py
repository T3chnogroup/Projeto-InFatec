import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv
from werkzeug.local import F
load_dotenv(".env")

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)

def delete_post(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM post WHERE id_post = %s", [id])
    mysql.connection.commit()
    cur.close()



def edit_post(id_post,conteudo,titulo_post):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE post SET conteudo=%s,titulo_post=%s WHERE id_post=%s", (conteudo,titulo_post,id_post))
    mysql.connection.commit()
    cur.close()


def getPosts(id_canal, id_usuario):
    cur = mysql.connection.cursor()
    conteudo = cur.execute(f'''select *, u.nome as criador from post p
    right join usuario u on p.fk_usuario=u.id_usuario
    left join anexo a on a.fk_post=p.id_post
    where p.fk_canal={id_canal} and 
    p.id_post NOT IN(
        select vp.fk_post from post p
        inner join visualizado_por vp
        on p.id_post=vp.fk_post
        where vp.fk_usuario={id_usuario} and p.fk_canal={id_canal}
    )''')
    Posts = cur.fetchall()
    cur.close()
    return Posts


def insere_post(id_canal, conteudo, date, titulo_post, id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO post(id_post, data_postagem, conteudo, fk_canal, fk_usuario, titulo_post) VALUES (%s, %s, %s, %s, %s, %s)", (0, str(date.today()), conteudo, id_canal, id_usuario, titulo_post))
    mysql.connection.commit()
    id = cur.lastrowid
    cur.close()
    return id


def salva_arquivo(id_post, arquivo):
    cur = mysql.connection.cursor()
    cur.execute("INSERT into anexo(nome, fk_post) values(%s, %s)",(arquivo, str(id_post)))
    mysql.connection.commit()
    cur.close()


def insere_visualizado(id_post, usuario, date):
    cur = mysql.connection.cursor()
    cur.execute("INSERT into visualizado_por(fk_usuario, fk_post, data_visualizacao) values(%s, %s, %s)",(str(usuario),str(id_post),str(date.today())))
    mysql.connection.commit()
    cur.close()

def posts_visualizado(id_usuario, id_canal):
    cur = mysql.connection.cursor()
    conteudo = cur.execute(f'''select p.*, a.nome, u.nome as criador from post p
        left join anexo a
        on p.id_post=a.fk_post
        inner join visualizado_por vp
        on p.id_post=vp.fk_post
        inner join usuario u
        on u.id_usuario=p.fk_usuario
        where vp.fk_usuario={id_usuario}
        and p.fk_canal={id_canal}''')
    Posts = cur.fetchall()
    cur.close()
    return Posts

def volta_visualizado(id_post,id_usuario):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM visualizado_por WHERE fk_post = %s AND fk_usuario = %s", [id_post, id_usuario])
    mysql.connection.commit()
    cur.close()