from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
# app.config['MYSQL_Host'] = 'localhost'
app.config['MYSQL_HOST'] = '0.0.0.0'
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'dsm!123456'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'infatec'

mysql = MySQL(app)

def getPosts():
    cursor = mysql.connection.cursor()
    conteudo = cursor.execute("SELECT * FROM post")
    Posts = cursor.fetchall()
    return Posts

def getChannel(id_canal):
    cursor = mysql.connection.cursor()
    cur = cursor.execute("SELECT nome FROM canal where id_canal = %s", (id_canal,)) # Pega o nome do canal que veio da url
    nome_canal = cursor.fetchall()[0][0]
    return nome_canal

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # fazer aqui validação de login
        email = 'elen.petri@fatec.sp.gov.br'
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

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == "POST":
        id_canal = request.args.get('canal')
        
        conteudo = request.form['post']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO post(id_post, data_postagem, data_expiracao, conteudo, fk_canal, fk_usuario) VALUES (%s, %s, %s, %s, %s, %s)", (0, str(date.today()), str(date.today()), conteudo, id_canal, None))
        mysql.connection.commit()
        Posts = getPosts()

        cur.close()
        return render_template('posts.html', id_canal=id_canal,Posts=Posts, canais=getcanais(), titulocanal=getChannel(id_canal))
    elif request.method == "GET": 
        id_canal = request.args.get('canal')

        Posts = getPosts()

        return render_template("posts.html", id_canal=id_canal, Posts=Posts, canais=getcanais(), titulocanal =getChannel(id_canal))

    return render_template('posts.html', id_canal=id_canal)

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
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO canal(nome, grupo, semestre, curso) VALUES (%s, %s, %s, %s)", (nome, grupo, semestre, curso))
       
    mysql.connection.commit()
        
    cur.close()
    cursor = mysql.connection.cursor()
    cur = cursor.execute("SELECT max(id_canal) FROM canal where nome = %s", (nome,)) # Select utilizado por ter nomes de canal duplicado
    idcanal = cursor.fetchall()[0]
    return redirect(url_for('post', canal = idcanal))