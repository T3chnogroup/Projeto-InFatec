from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date

app = Flask(__name__)

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_HOST'] = '0.0.0.0'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'infatec'
# app.config[''] = '33060'

mysql = MySQL(app)

def retornoPosts(cur): 
    conteudo = cur.execute("SELECT * FROM post")
    Posts = cur.fetchall()
    return Posts

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
        conteudo = request.form['post']
        print(conteudo)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO post(id_post, data_postagem, data_expiracao, conteudo, fk_canal, fk_usuario) VALUES (%s, %s, %s, %s, %s, %s)", (0, str(date.today()), str(date.today()), conteudo, None, None))
        mysql.connection.commit()
        Posts = retornoPosts(cur)
        cur.close()
        return render_template('posts.html', Posts=Posts)
    elif request.method == "GET": 
        cur = mysql.connection.cursor()
        Posts = retornoPosts(cur)

        return render_template("posts.html", Posts=Posts)

    return render_template('posts.html')

@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    return render_template('gerenciamento_usuario.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')