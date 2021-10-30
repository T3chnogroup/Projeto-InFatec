import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv
from gerenciamento_post.post import getPosts, insere_post
from gerenciamento_post.delete import delete_post
from gerenciamento_post.edit import edit_post

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

'''def getPosts(id_canal): 
    cursor = mysql.connection.cursor()
    conteudo = cursor.execute(f'SELECT * FROM post where fk_canal={id_canal} order by id_post desc')
    Posts = cursor.fetchall()
    return Posts '''

def getChannel(id_canal):
    cursor = mysql.connection.cursor()
    cur = cursor.execute("SELECT nome FROM canal where id_canal = %s", (id_canal,)) # Pega o nome do canal que veio da url
    nome_canal = cursor.fetchall()[0][0]
    return nome_canal

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # fazer aqui validação de login
        cursor = mysql.connection.cursor()
        cpf = request.form['login']
        cur = cursor.execute("select email from usuario where cpf = %s", (cpf,)) # Recupera e-mail a partir do cpf
        if cursor.rowcount > 0:
            lista_emails = cursor.fetchall()
            return redirect(url_for('inicio', email = lista_emails[0][0]))
        else:
            return redirect(url_for('inicio'))
    else:
        return render_template('login.html')

@app.route('/redefinir')
def redefinir():
    return render_template('redefinir_senha.html')

def getcanais():
    cursor = mysql.connection.cursor()
    cur = cursor.execute("SELECT id_canal, nome FROM canal") # Seleciona a coluna id e a colona nome do canal na tabela
    return cursor.fetchall()

@app.route('/')
def inicio():
    return render_template('home.html', canais=getcanais(), )

@app.route('/post/<id_edit>', methods=['POST'])
def editar_post(id_edit):
    conteudo = request.form['text-editar-post']
    edit_post(id_edit,conteudo)
    id_canal = request.args.get('canal')
    posts= getPosts(id_canal)
    return render_template('posts.html', id_canal=id_canal,Posts=posts, canais=getcanais(), titulocanal=getChannel(id_canal), pode_editar = True)

@app.route('/post', methods=['GET', 'POST'])
def post():
    id_canal = request.args.get('canal')
    if request.method == "POST":  
        conteudo = request.form['post']
        posts = insere_post(id_canal,conteudo,date)
        
        return render_template('posts.html', id_canal=id_canal,Posts=posts, canais=getcanais(), titulocanal=getChannel(id_canal), pode_editar = True)
        

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

@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    return render_template('gerenciamento_usuario.html', canais=getcanais(), titulocanal = "Gerenciamento Usuários")

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/criarcanal', methods = ['POST'])
def criar_canal():
    data = request.form 
    nome = data['nome']
    grupo = data['grupo']
    semestre = data['semestre']
    curso = data['curso']
    emails = data.getlist('email')
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO canal(nome, grupo, semestre, curso) VALUES (%s, %s, %s, %s)", (nome, grupo, semestre, curso))
    cur.execute("SELECT max(id_canal) FROM canal where nome = %s", (nome,)) # Select utilizado por ter nomes de canal duplicado
    id_canal = cur.fetchall()[0]

    #Saber qual o id do usuário
    for email in emails:
        cur.execute("SELECT id_usuario from usuario where email = %s", (email,)) # busca o id do usuario com este email no banco
        if cur.rowcount > 0:# se existir esse id
            id_usuario = cur.fetchall()[0][0]
            cur.execute("INSERT INTO canal_usuario(id_canal, id_usuario) VALUES (%s, %s)", (id_canal, id_usuario)) #inserir na tabela canal_usuario

    mysql.connection.commit()
        
    cur.close()
    
    return redirect(url_for('post', canal = id_canal))

@app.route('/delete_post/<id_canal>/<id_post>')
def delete_post_by_id(id_canal,id_post): 
    delete_post(id_post)
    return redirect(url_for('post',canal=id_canal))
   