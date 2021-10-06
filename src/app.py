from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_Host'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '*****'
app.config['MYSQL_DB'] = 'infatec'

mysql = MySQL(app)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # fazer aqui validação de login
        return redirect(url_for('inicio'))
    else:
        return render_template('login.html')

@app.route('/redefinir')
def redefinir():
    return render_template('redefinir_senha.html')

@app.route('/')
def inicio():
    return render_template('home.html')

@app.route('/post')
def post():
    return render_template('posts.html')

@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    return render_template('gerenciamento_usuario.html')

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
    
    # cur = mysql.connection.cursor()
    # cur.execute("INSERT INTO canal(nome, fk_usuario) VALUES (%s, %s)", (nome, fk_usuario))
       
    # mysql.connection.commit()
        
    # cur.close()

    return render_template('home.html')