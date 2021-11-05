import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from dotenv import load_dotenv
from functions import validatePassword
from models import usuario

from gerenciamento.gerenciamento_post import getPosts, insere_post, delete_post, edit_post
from werkzeug.utils import secure_filename
from gerenciamento.gerenciamento_post import salva_arquivo
from gerenciamento_canal import adicionar_lista_emails, deixa_de_seguir, excluir_canal, listar_moderador, listar_participante, alterar_funcao_membro, remover_membros, getcanais, segue_canal, seguir
from gerenciamento_usuario import editar_permissoes, listar_usuario, pode_criar_canais, pode_gerenciar_usuarios, remover_usuario
load_dotenv(".env")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)      
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# configuração Conexão com o Banco de Dados Mysql
# app.config['MYSQL_Host'] = os.getenv("MYSQL_Host")
app.config['MYSQL_HOST'] = '0.0.0.0'
# app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL(app)



def getChannel(id_canal):
    cursor = mysql.connection.cursor()
    cur = cursor.execute("SELECT nome FROM canal where id_canal = %s", (id_canal,)) # Pega o nome do canal que veio da url
    nome_canal = cursor.fetchall()[0][0]
    return nome_canal

def getVerificaFuncao (id_canal):
    # pegar o email do usuário a partir do cookie 
    email_logado = request.cookies.get('email_logado')
    # descobrir id do usuário a partir do email
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_usuario from usuario where email = %s", (email_logado,)) # busca o id do usuario com este email no banco
    if cur.rowcount > 0:# se existir esse id
        id_usuario = cur.fetchall()[0][0]
    # verificar a existencia de uma linha na tabela canal_usuario para este usuário e este canal
        cur.execute("select * from canal_usuario where id_canal = %s and id_usuario = %s and funcao = 'moderador'", (id_canal, id_usuario))
        return cur.rowcount > 0
    return False

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # fazer aqui validação de login
        cursor = mysql.connection.cursor()
        cpf = request.form['login']
        password = request.form['password']
        cur = cursor.execute("select email from usuario where cpf = %s and senha = %s", (cpf,password)) # Recupera e-mail a partir do cpf
        if cursor.rowcount > 0:
            lista_emails = cursor.fetchall()
            return redirect(url_for('inicio', email = lista_emails[0][0]))
        else:
            return render_template('login.html')
    else:
        if recuperar_id_usuario_logado() != None:
            return redirect(url_for('inicio'))
        return render_template('login.html')

@app.route('/redefinir')
def redefinir():
    return render_template('redefinir_senha.html')

@app.route('/')
def inicio():
    if recuperar_id_usuario_logado() == None:
        return redirect(url_for('login'))
    return render_template('home.html', canais=getcanais(recuperar_id_usuario_logado()), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()) )

@app.route('/post/<id_edit>', methods=['POST'])
def editar_post(id_edit):
    conteudo = request.form['text-editar-post']
    titulo = request.form['titulo']
    edit_post(id_edit,conteudo,titulo)
    id_canal = request.args.get('canal')
    posts= getPosts(id_canal)
    return render_template('posts.html', id_canal=id_canal,Posts=posts, canais=getcanais(recuperar_id_usuario_logado()), titulocanal=getChannel(id_canal), pode_editar = True, pode_deletar = True)

@app.route('/post', methods=['GET', 'POST'])
def post():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    seguidor = segue_canal(id_canal, id_usuario) #Saber se o usuário é seguidor ou não
    if request.method == "POST":   
        conteudo = request.form['post']
        arquivo = request.files['arquivo']
        titulo_post = request.form['titulo']
        id_post = insere_post(id_canal,conteudo,date, titulo_post)
        if arquivo and allowed_file(arquivo.filename):
            filename = str(id_post)+'_'+secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            salva_arquivo(id_post, filename)
            
        posts=getPosts(id_canal)
        return render_template('posts.html', id_canal=id_canal,Posts=posts, canais=getcanais(id_usuario), titulocanal=getChannel(id_canal), pode_editar = True, pode_deletar = True, seguidor=seguidor, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()))
    elif request.method == "GET": 
        if getVerificaFuncao (id_canal):
            pode_editar = True
            pode_deletar = True
        else:
            pode_editar = False
            pode_deletar = False
        Posts = getPosts(id_canal)
        return render_template("posts.html", id_canal=id_canal, seguidor = seguidor, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), titulocanal =getChannel(id_canal), pode_editar = pode_editar, pode_deletar = pode_deletar, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()))

    return render_template('posts.html', id_canal= id_canal, pode_editar = False)

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        password = request.form['password']
        confirmacao_senha = request.form['confirmacao_senha']
        cur = mysql.connection.cursor()
        if usuario.registeredEmail(cur, mysql, email):
            return render_template('cadastro.html', erro = 'Email já cadastrado')
        if usuario.registeredCpf(cur, mysql, cpf):
            return render_template('cadastro.html', erro = 'CPF já cadastrado')
        if validatePassword.validatePassword(password, confirmacao_senha):
            usuario.insertUser(cur, mysql, nome, email, password, cpf)
            return render_template('cadastro.html', resposta = 'True')   
        else:
            return render_template('cadastro.html', erro = 'Senhas incompativeis')
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

@app.route('/delete_post/<id_canal>/<id_post>')
def delete_post_by_id(id_canal,id_post): 
    delete_post(id_post)
    return redirect(url_for('post',canal=id_canal))
   

#Configurações do Canal
@app.route('/gerenciamento-canal')
def configuracao_canal():
    id_canal = request.args.get('canal')
    moderadores = listar_moderador(id_canal)
    participantes = listar_participante(id_canal)
    nome_canal = getChannel(id_canal)
    return render_template('gerenciamento_canal.html', id_canal=id_canal, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = nome_canal,  moderadores = moderadores, participantes = participantes, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()))

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
    if email_logado == None or email_logado == '':
        email_logado = request.args.get('email')
    if email_logado == None or email_logado == '':
        return None
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


#Gerenciamento de usuários
@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    Usuarios = listar_usuario()    
    return render_template('gerenciamento_usuario.html', usuarios = Usuarios, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = "Gerenciamento Usuários", pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()))

@app.route('/remover_usuario', methods = ['POST'])
def removerUsuarios():
    id_usuario = request.args.get('usuario')
    remover_usuario(id_usuario)
    return redirect(url_for('gerenciamentoUsuario'))

@app.route('/editar_permissoes', methods = ['POST'])
def permissoes_usuarios():
    id_usuario = request.args.get('usuario')
    pode_gerenciar_usuario = request.form.get('gerenciar_usuarios')
    if pode_gerenciar_usuario == None:
        pode_gerenciar_usuario = 0
    pode_criar_canais = request.form.get('criar_canais')
    if pode_criar_canais == None:
        pode_criar_canais = 0
    editar_permissoes(id_usuario, pode_gerenciar_usuario, pode_criar_canais)
    return redirect(url_for('gerenciamentoUsuario'))

