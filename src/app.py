import os
from flask import Flask, render_template, request, url_for, redirect
from flask_mysqldb import MySQL
from datetime import date
from hashlib import sha1
from dotenv import load_dotenv

from .functions.validatePassword import validate_password

from .models import usuario

from .gerenciamento import getPosts, insere_post, delete_post, edit_post
from werkzeug.utils import secure_filename
from .gerenciamento import salva_arquivo, insere_visualizado, posts_visualizado, volta_visualizado
from .gerenciamento import adicionar_lista_emails, desafixa_canal, excluir_canal, listar_moderador, listar_participante, alterar_funcao_membro, remover_membros, getcanais, canal_fixado, fixar_canal
from .gerenciamento import editar_permissoes, listar_usuario, pode_criar_canais, pode_gerenciar_usuarios, remover_usuario, editar_visibilidade,recuperar_visibilidade_canal, criar_canal, retorna_cursos, retorna_grupos

load_dotenv(".env")

UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)      
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# configuração Conexão com o Banco de Dados Mysql
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")

mysql = MySQL()
mysql.init_app(app)

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
    # verificar a existencia 3de uma linha na tabela canal_usuario para este usuário e este canal
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
        cur = cursor.execute("select email from usuario where cpf = %s and senha = %s", (cpf,sha1(password.encode('utf-8')).hexdigest())) # Recupera e-mail a partir do cpf
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
    return render_template('home.html', canais=getcanais(recuperar_id_usuario_logado()), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario())

@app.route('/post/<id_edit>', methods=['POST'])
def editar_post(id_edit):
    conteudo = request.form['text-editar-post']
    titulo = request.form['titulo']
    edit_post(id_edit,conteudo,titulo)
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o canal é fixado ou não

    posts= getPosts(id_canal, id_usuario)
    return redirect(url_for('post',canal=id_canal))

@app.route('/post', methods=['GET', 'POST'])
def post():
    id_canal = request.args.get('canal')
    grupos = retorna_grupos(id_canal)
    cursos = retorna_cursos(id_canal)
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o canal é fixado ou não
    if request.method == "POST":   
        conteudo = request.form['post']
        arquivo = request.files['arquivo']
        titulo_post = request.form['titulo']
        id_post = insere_post(id_canal,conteudo,date, titulo_post)
        if arquivo and allowed_file(arquivo.filename):
            filename = str(id_post)+'_'+secure_filename(arquivo.filename)
            arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            salva_arquivo(id_post, filename)
        posts=getPosts(id_canal, id_usuario)
        return render_template('posts.html', id_canal=id_canal,Posts=posts, canais=getcanais(id_usuario), titulocanal=getChannel(id_canal), pode_editar = True, pode_deletar = True, fixado=fixado, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), lista_de_grupos = grupos, lista_de_cursos = cursos, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))
    elif request.method == "GET": 
        if getVerificaFuncao (id_canal):
            pode_editar = True
            pode_deletar = True
        else:
            pode_editar = False
            pode_deletar = False
        Posts = getPosts(id_canal, id_usuario)
        return render_template("posts.html", id_canal=id_canal, fixado = fixado, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), titulocanal =getChannel(id_canal), pode_editar = pode_editar, pode_deletar = pode_deletar, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), lista_de_grupos = grupos, lista_de_cursos = cursos, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

    return render_template('posts.html', id_canal= id_canal, pode_editar = False, visibilidade_canal = recuperar_visibilidade_canal(id_canal))

@app.route('/posts_visualizado')
def posts_visualizados():
    id_canal = request.args.get('canal')
    grupos = retorna_grupos(id_canal)
    cursos = retorna_cursos(id_canal)
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o canal é fixado ou não
    if not getVerificaFuncao (id_canal):
        pode_editar = False
        pode_deletar = False
    Posts = posts_visualizado(id_usuario, id_canal)
    return render_template("posts_visualizado.html", id_canal=id_canal, fixado = fixado, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), titulocanal =getChannel(id_canal), pode_editar = pode_editar, pode_deletar = pode_deletar, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), lista_de_grupos = grupos, lista_de_cursos = cursos, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

@app.route('/deixar_visualizado/<id_post>', methods = ['GET'])
def voltar_de_visualizar(id_post):
    id_canal = request.args.get('canal')
    volta_visualizado(id_post)
    return redirect(url_for('posts_visualizados', canal = id_canal))

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
        if validate_password(password, confirmacao_senha):
            usuario.insertUser(cur, mysql, nome, email, sha1(password.encode('utf-8')).hexdigest(), cpf)
            return render_template('cadastro.html', resposta = 'True')   
        else:
            return render_template('cadastro.html', erro = 'Senhas incompativeis')
    return render_template('cadastro.html')

@app.route('/criarcanal', methods = ['POST'])
def rota_criar_canal():
    data = request.form 
    nome = data['nome']
    visibilidade = data['visibilidade']
    emails = data.getlist('email')
    grupos = data.getlist('grupo')
    cursos = data.getlist('curso')
    id_canal = criar_canal(nome, visibilidade, emails, grupos, cursos)
    return redirect(url_for('post', canal = id_canal))

#mais recentes
@app.route('/mais_recentes', methods = ['GET'])
def mais_recentes():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o usuário é fixado ou não

    if request.method == "GET":
        print(request.form)   
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from post where fk_canal = %s order by data_postagem desc", (id_canal,)) # busca da data da postagem  

        if getVerificaFuncao (id_canal):
            pode_editar = True
            pode_deletar = True
        else:
            pode_editar = False
            pode_deletar = False

        if cur.rowcount > 0:# se existir esta postagem
            Posts = cur.fetchall()
            
            cur.close()

            return render_template('posts.html', id_canal=id_canal, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), fixado=fixado, pode_editar=pode_editar, pode_deletar=pode_deletar, titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

    return render_template('posts.html', id_canal= id_canal, mais_recentes = False, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

#mais antigas
@app.route('/mais_antigas', methods = ['GET'])
def mais_antigas():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o usuário é fixado ou não

    if getVerificaFuncao (id_canal):
            pode_editar = True
            pode_deletar = True
    else:
            pode_editar = False
            pode_deletar = False

    if request.method == "GET":
        print(request.form)   
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from post where fk_canal = %s order by data_postagem asc", (id_canal,)) # busca da data da postagem  
        if cur.rowcount > 0:# se existir esta postagem
            Posts = cur.fetchall()
            
            cur.close()

            return render_template('posts.html', id_canal=id_canal, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), fixado=fixado,pode_editar=pode_editar, pode_deletar=pode_deletar, titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

    return render_template('posts.html', id_canal= id_canal, mais_antigas = False, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

# pesquisa avançada
@app.route('/pesquisa_postagem', methods = ['GET', 'POST'])
def pesquisa_postagem():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o usuário é fixado ou não

    if getVerificaFuncao (id_canal):
        pode_editar = True
        pode_deletar = True
    else:
        pode_editar = False
        pode_deletar = False

    if request.method == "POST":
        print(request.form)   
        query = ""
        titulo = request.form['titulo']
        data_inicial = request.form['data_inicial']
        data_final = request.form['data_final']
        if titulo != "":
            query = "where titulo_post like '%{0}%'".format(titulo)
        
        else:
            query = "where data_postagem BETWEEN '{0}' and '{1}'".format(data_inicial, data_final)
        print(query)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from post {0}".format(query)) # busca do titulo ou da data da postagem 
        if cur.rowcount > 0:# se existir esta postagem
            Posts = cur.fetchall()

            mysql.connection.commit()
            
            cur.close()
            print (Posts)
        return render_template('posts.html', id_canal=id_canal, Posts=Posts, fixado=fixado,pode_editar=pode_editar, pode_deletar=pode_deletar, canais=getcanais(recuperar_id_usuario_logado()), titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

    return render_template('posts.html', id_canal= id_canal, pesquisa_postagem = False, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

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
    visibilidade_canal = recuperar_visibilidade_canal(id_canal)
    return render_template('gerenciamento_canal.html', id_canal=id_canal, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = nome_canal,  moderadores = moderadores, participantes = participantes, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), visibilidade_canal=visibilidade_canal, emails = listar_usuario())

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

@app.route('/desafixar-canal', methods = ['POST'])
def desafixar_canal():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    desafixa_canal(id_canal, id_usuario)
    return redirect(url_for('inicio'))

@app.route('/fixar-canal', methods = ['Post'])
def rota_fixar_canal():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixar_canal (id_canal, id_usuario)
    return redirect(url_for('post', canal = id_canal))

@app.route('/insere_visualizado/<id_post>', methods = ['GET'])
def deixar_de_visualizar(id_post):
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    insere_visualizado(id_post, id_usuario, date)
    return redirect(url_for('post', canal = id_canal))

#Gerenciamento de usuários
@app.route('/gerenciamento_usuario')
def gerenciamentoUsuario():
    Usuarios = listar_usuario()    
    return render_template('gerenciamento_usuario.html', usuarios = Usuarios, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = "Gerenciamento Usuários", pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario())

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

#Gerenciamento da visibilidade do canal (Público / Privado)
@app.route('/editar_canal', methods = ['POST'])
def editar_canal():
    id_canal = request.args.get('canal')
    visibilidade_canal = request.form.get('visibilidade_canal')
    editar_visibilidade(id_canal, visibilidade_canal)
    return redirect(url_for('configuracao_canal', canal=id_canal))
