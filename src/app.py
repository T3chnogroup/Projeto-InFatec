import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv

from gerenciamento_canal import adicionar_lista_emails, deixa_de_seguir, excluir_canal, listar_moderador, listar_participante, alterar_funcao_membro, remover_membros, getcanais, segue_canal, seguir
from gerenciamento_usuario import listar_usuario
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
    conteudo = cursor.execute(f'SELECT * FROM post where fk_canal={id_canal} order by id_post desc')
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

@app.route('/')
def inicio():
    return render_template('home.html', canais=getcanais(recuperar_id_usuario_logado()), )

@app.route('/post', methods=['GET', 'POST'])
def post():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    seguidor = segue_canal(id_canal, id_usuario) #Saber se o usuário é seguidor ou não
    if request.method == "POST":   
        conteudo = request.form['post']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO post(id_post, data_postagem, data_expiracao, conteudo, fk_canal, fk_usuario) VALUES (%s, %s, %s, %s, %s, %s)", (0, str(date.today()), str(date.today()), conteudo, id_canal, None))
        mysql.connection.commit()
        Posts = getPosts(id_canal)

        cur.close()
        return render_template('posts.html', id_canal=id_canal,Posts=Posts, canais=getcanais(id_usuario), titulocanal=getChannel(id_canal), pode_editar = True, seguidor=seguidor)
    elif request.method == "GET": 
        cur = mysql.connection.cursor()
        # verificar a existencia de uma linha na tabela canal_usuario para este usuário e este canal
        cur.execute("select * from canal_usuario where id_canal = %s and id_usuario = %s and funcao = 'moderador'", (id_canal, id_usuario))
        if cur.rowcount > 0:
            pode_editar = True
        else:
            pode_editar = False
        Posts = getPosts(id_canal)
        return render_template("posts.html", id_canal=id_canal, seguidor = seguidor, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), titulocanal =getChannel(id_canal), pode_editar = pode_editar)

    return render_template('posts.html', id_canal= id_canal, pode_editar = False)

@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    Usuarios = listar_usuario()    
    return render_template('gerenciamento_usuario.html', usuarios = Usuarios, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = "Gerenciamento Usuários")

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
    visibilidade = data['visibilidade']
    emails = data.getlist('email')
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO canal(nome, grupo, semestre, curso, visibilidade) VALUES (%s, %s, %s, %s, %s)", (nome, grupo, semestre, curso, visibilidade))
    cur.execute("SELECT max(id_canal) FROM canal where nome = %s", (nome,)) # Select utilizado por ter nomes de canal duplicado
    id_canal = cur.fetchall()[0]

    #Saber qual o id do usuário
    email_logado = request.cookies.get('email_logado')
    adicionar_lista_emails(emails, id_canal, email_logado) # adicona a lista de emails ao canal
    cur.execute("SELECT id_usuario from usuario where email = %s", (email_logado,)) # busca o id do usuario com este email no banco
    if cur.rowcount > 0:# se existir esse id
        id_usuario = cur.fetchall()[0][0]
        cur.execute("INSERT INTO canal_usuario(id_canal, id_usuario, funcao) VALUES (%s, %s, 'moderador')", (id_canal, id_usuario)) #inserir na tabela canal_usuario como moderador

    mysql.connection.commit()
        
    cur.close()
    
    return redirect(url_for('post', canal = id_canal))


#Configurações do Canal
@app.route('/gerenciamento-canal')
def configuracao_canal():
    id_canal = request.args.get('canal')
    moderadores = listar_moderador(id_canal)
    participantes = listar_participante(id_canal)
    nome_canal = getChannel(id_canal)
    return render_template('gerenciamento_canal.html', id_canal=id_canal, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = nome_canal,  moderadores = moderadores, participantes = participantes)

@app.route('/adicionar-membros', methods = ['POST'])
def adicionar_membros():
    id_canal = request.args.get('canal')
    emails = request.form.getlist('email')
    email_logado = request.cookies.get('email_logado')
    adicionar_lista_emails(emails, id_canal, email_logado) # adiciona a lista de emails ao canal
    return redirect(url_for('configuracao_canal', canal = id_canal))

@app.route('/editar-funcao-membro-canal')
def alterar_funcao_membro_canal():
    id_usuario = request.args.get('usuario')
    id_canal = request.args.get('canal')
    funcao = request.args.get('funcao')
    alterar_funcao_membro(id_usuario, id_canal, funcao)
    return redirect(url_for('configuracao_canal', canal = id_canal))

@app.route('/remover-membros', methods = ['POST'])
def remover_membros_canal():
    id_usuario = request.args.get('usuario')
    id_canal = request.args.get('canal')
    remover_membros(id_usuario, id_canal)
    return redirect(url_for('configuracao_canal', canal = id_canal))

@app.route('/excluir_canal', methods = ['POST'])
def exclusao_canal():
    id_canal = request.args.get('canal')
    excluir_canal(id_canal)
    return redirect(url_for('inicio'))

def recuperar_id_usuario_logado():
    # pegar o email do usuário a partir do cookie 
    email_logado = request.cookies.get('email_logado')
    # descobrir id do usuário a partir do email
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario from usuario where email = %s", (email_logado,)) # busca o id do usuario com este email no banco
    if cur.rowcount > 0:# se existir esse id
        id_usuario = cur.fetchall()[0][0]
        return id_usuario
    else:
        return None

@app.route('/deixar-de-seguir', methods = ['POST'])
def deixar_de_seguir():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    deixa_de_seguir(id_canal, id_usuario)
    return redirect(url_for('post', canal = id_canal))

@app.route('/seguir', methods = ['Post'])
def rota_seguir():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    seguir (id_canal, id_usuario)
    return redirect(url_for('post', canal = id_canal))
