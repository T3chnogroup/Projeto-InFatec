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

def getPosts(id_canal):
    cursor = mysql.connection.cursor()
    conteudo = cursor.execute(f'SELECT * FROM post left join anexo on anexo.fk_post=post.id_post where fk_canal={id_canal} order by id_post desc')
    Posts = cursor.fetchall()
    return Posts

def insere_post (id_canal, conteudo, date):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO post(id_post, data_postagem, data_expiracao, conteudo, fk_canal, fk_usuario) VALUES (%s, %s, %s, %s, %s, %s)", (0, str(date.today()), str(date.today()), conteudo, id_canal, None))
    mysql.connection.commit()
    Posts = getPosts(id_canal)
    id = cur.lastrowid
    cur.close()
    return [Posts, id]


@app.route('/post', methods=['GET', 'POST'])
def post():
    id_canal = request.args.get('canal')
    if request.method == "POST":   
        conteudo = request.form['post']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO post(id_post, data_postagem, data_expiracao, conteudo, fk_canal, fk_usuario) VALUES (%s, %s, %s, %s, %s, %s)", (0, str(date.today()), str(date.today()), conteudo, id_canal, None))
        mysql.connection.commit()
        Posts = getPosts(id_canal)

        cur.close()
        return render_template('posts.html', id_canal=id_canal,Posts=Posts, canais=getcanais(), titulocanal=getChannel(id_canal), pode_editar = True)
    elif request.method == "GET": 
        # pegar o email do usuário a partir do cookie 
        email_logado = request.cookies.get('email_logado')
        # descobrir id do usuário a partir do email
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_usuario from usuario where email = %s", (email_logado,)) # busca o id do usuario com este email no banco
        if cur.rowcount > 0:# se existir esse id
            id_usuario = cur.fetchall()[0][0]
        # verificar a existencia de uma linha na tabela canal_usuario para este usuário e este canal
            cur.execute("select * from canal_usuario where id_canal = %s and id_usuario = %s", (id_canal, id_usuario))
        if cur.rowcount > 0:
            pode_editar = True
        else:
            pode_editar = False
        Posts = getPosts(id_canal)

        return render_template("posts.html", id_canal=id_canal, Posts=Posts, canais=getcanais(), titulocanal =getChannel(id_canal), pode_editar = pode_editar)

    return render_template('posts.html', id_canal= id_canal, pode_editar = False)


