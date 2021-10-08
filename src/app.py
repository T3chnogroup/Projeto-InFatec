from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_Host'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
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

@app.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == "POST":
        conteudo = request.form['conteudo']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO post(conteudo) VALUES (%s)", (conteudo))
        mysql.connection.commit()
        cur.close()

        return 'sucesso'

    elif request.method == "GET": 
        cur = mysql.connection.cursor()
        conteudo = cur.execute("SELECT * FROM post")

        if conteudo > 0:
            Conteudos = cur.fetchall()

        return render_template("posts.html", Conteudos=Conteudos)

    return render_template('posts.html')

@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    return render_template('gerenciamento_usuario.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')