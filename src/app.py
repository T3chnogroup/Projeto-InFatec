import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_mysqldb import MySQL
from datetime import date
from hashlib import sha1
from dotenv import load_dotenv
from flask_mail import Mail, Message

from .functions.validatePassword import validate_password

from .models import usuario

from .gerenciamento import getPosts, insere_post, delete_post, edit_post
from werkzeug.utils import secure_filename
from .gerenciamento import salva_arquivo, insere_visualizado, posts_visualizado, volta_visualizado
from .gerenciamento import adicionar_lista_emails, desafixa_canal, excluir_canal, listar_moderador, listar_participante, alterar_funcao_membro, remover_membros, getcanais, canal_fixado, fixar_canal
from .gerenciamento import editar_permissoes, listar_usuario, pode_criar_canais, pode_gerenciar_usuarios, remover_usuario, editar_visibilidade,recuperar_visibilidade_canal, criar_canal, retorna_cursos, retorna_grupos, alunos_selecionados, coordenadores_selecionados, professores_selecionados, lista_cursos, editar_destinatarios_canal
from .gerenciamento import busca_user_id, editando_usuario

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

# configuração email
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 't3chnogroup3@gmail.com'
app.config['MAIL_PASSWORD'] = 'Grupo3fatec'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mysql = MySQL()
mysql.init_app(app)

mail = Mail(app)

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

@app.route('/confirmacao_email')
def confirmacao_email():
    id_usuario = request.args.get('id_usuario')
    cursor = mysql.connection.cursor()
    if usuario.validUser(cursor, id_usuario):
        return render_template('login.html', validado = False)
    else:
        usuario.validateUser(cursor, mysql, id_usuario)
        return render_template('login.html', validado = True)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # fazer aqui validação de login
        cursor = mysql.connection.cursor()
        cpf = request.form['login']
        password = request.form['password']
        cur = cursor.execute("select email from usuario where cpf = %s and senha = %s and valido = 1", (cpf,sha1(password.encode('utf-8')).hexdigest())) # Recupera e-mail a partir do cpf
        if cursor.rowcount > 0:
            lista_emails = cursor.fetchall()
            return redirect(url_for('inicio', email = lista_emails[0][0]))
        else:
            return render_template('login.html')
    else:
        if recuperar_id_usuario_logado() != None:
            return redirect(url_for('inicio'))
        return render_template('login.html')

@app.route('/redefinir', methods=['POST', 'GET'])
def redefinir():
    if request.method == 'POST':
        email = request.form['email']
        cur = mysql.connection.cursor()
        if not usuario.registeredEmail(cur, email):
            return render_template('redefinir_senha.html', erro='Email ainda não cadastrado')
        else:
            email_usuario = usuario.searchUserByEmail(cur, email)
            usuario.sendConfirmationEmail(Message, mail, email, f'Redefina sua senha neste link: http://localhost:5000/redefinir_senha?id_usuario={email_usuario[0]}')
            cur.close()
            return render_template('redefinir_senha.html', resposta='True')
    return render_template('redefinir_senha.html')

# Rotas para gerenciar perfil

@app.route('/gerenciamento_perfil')
def gerenciamento_perfil():
    id_usuario = recuperar_id_usuario_logado()
    usuario_logado = busca_user_id(id_usuario)
    return render_template('gerenciamento_perfil.html', 
    usuario_logado = usuario_logado, canais=getcanais(id_usuario), 
    pode_criar_canal = pode_criar_canais(id_usuario), 
    pode_gerenciar_usuario = pode_gerenciar_usuarios(id_usuario), titulocanal = "Gerenciamento de perfil")


@app.route('/editar',methods=['POST','GET'])
def editar_perfil():

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        editando_usuario(nome, email, cpf, recuperar_id_usuario_logado())
    return redirect(url_for('gerenciamento_perfil'))


@app.route('/home')
def home():
    return render_template('home.html')
    
@app.route('/redefinir_senha', methods=['GET', 'POST'])
def redefinir_by_id():
    if not pode_recuperar_senha():
        return redirect(url_for('login'))
    if request.method == 'POST':
        nova_senha = request.form['senha1']
        id_usuario = request.form['id_usuario']
        cur = mysql.connection.cursor()
        usuario.changePassword(cur, mysql, sha1(nova_senha.encode('utf-8')).hexdigest(), id_usuario)
        return redirect(url_for('login'))
    return render_template('nova_senha.html')

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
        id_post = insere_post(id_canal,conteudo,date, titulo_post, id_usuario)
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
    Posts = posts_visualizado(id_usuario, id_canal)
    return render_template("posts_visualizado.html", id_canal=id_canal, fixado = fixado, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), titulocanal =getChannel(id_canal), pode_editar = False, pode_deletar = False, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), lista_de_grupos = grupos, lista_de_cursos = cursos, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal))

@app.route('/deixar_visualizado/<id_post>', methods = ['GET'])
def voltar_de_visualizar(id_post):
    id_usuario = recuperar_id_usuario_logado()
    id_canal = request.args.get('canal')
    volta_visualizado(id_post, id_usuario)
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
        if usuario.registeredEmail(cur, email):
            return render_template('cadastro.html', erro = 'Email já cadastrado')
        if usuario.registeredCpf(cur, cpf):
            return render_template('cadastro.html', erro = 'CPF já cadastrado')
        if validate_password(password, confirmacao_senha):
            usuario.insertUser(cur, mysql, nome, email, sha1(password.encode('utf-8')).hexdigest(), cpf)
            cpf_usuario = usuario.searchUserByCpf(cur, cpf)
            usuario.sendConfirmationEmail(Message, mail, email, f'Confirme o seu cadastro: http://localhost:5000/confirmacao_email?id_usuario={cpf_usuario[0]}')
            cur.close()
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
    grupos = retorna_grupos(id_canal)
    cursos = retorna_cursos(id_canal)

    if getVerificaFuncao (id_canal):
         pode_editar = True
         pode_deletar = True
    else:
        pode_editar = False
        pode_deletar = False

    if request.method == "GET":
        print(request.form)   
        cur = mysql.connection.cursor()
        cur.execute("SELECT * from post where fk_canal = %s order by data_postagem desc", (id_canal,)) # busca da data da postagem  

        if cur.rowcount > 0:# se existir esta postagem
            Posts = cur.fetchall()
            
            cur.close()

            return render_template('posts.html', id_canal=id_canal, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), fixado=fixado, pode_editar=pode_editar, pode_deletar=pode_deletar, titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)

    return render_template('posts.html', id_canal=id_canal, mais_recentes = False, canais=getcanais(recuperar_id_usuario_logado()), fixado=fixado,pode_editar=pode_editar, pode_deletar=pode_deletar, titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()),pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)

#mais antigas
@app.route('/mais_antigas', methods = ['GET'])
def mais_antigas():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o usuário é fixado ou não
    grupos = retorna_grupos(id_canal)
    cursos = retorna_cursos(id_canal)

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

            return render_template('posts.html', id_canal=id_canal, Posts=Posts, canais=getcanais(recuperar_id_usuario_logado()), fixado=fixado, pode_editar=pode_editar, pode_deletar=pode_deletar, titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)
    
    return render_template('posts.html', id_canal=id_canal, mais_antigas = False, canais=getcanais(recuperar_id_usuario_logado()), fixado=fixado, pode_editar=pode_editar, pode_deletar=pode_deletar, titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()),pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)
   

# pesquisa avançada
@app.route('/pesquisa_postagem', methods = ['GET', 'POST'])
def pesquisa_postagem():
    id_canal = request.args.get('canal')
    id_usuario = recuperar_id_usuario_logado()
    fixado = canal_fixado(id_canal, id_usuario) #Saber se o usuário é fixado ou não
    grupos = retorna_grupos(id_canal)
    cursos = retorna_cursos(id_canal)

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
            query = "where c.id_canal={0} and p.titulo_post like '%{1}%'".format(id_canal, titulo)
        elif data_inicial != "" and data_final != '':
            query = "where c.id_canal={0} and p.data_postagem BETWEEN '{1}' and '{2}'".format(id_canal, data_inicial, data_final)
        elif data_inicial == "" and data_final != '':
            query = "where c.id_canal={0} and p.data_postagem='{1}'".format(id_canal, data_final)
        else:
            query = "where c.id_canal={0} and p.data_postagem='{1}'".format(id_canal, data_inicial)

        print(query)
        cur = mysql.connection.cursor()
        cur.execute("SELECT p.* from post p inner join canal c on p.fk_canal=c.id_canal {0}".format(query)) # busca do titulo ou da data da postagem 
        if cur.rowcount > 0:# se existir esta postagem
            Posts = cur.fetchall()

            mysql.connection.commit()
            
            cur.close()
            print (Posts)
            return render_template('posts.html', id_canal=id_canal, Posts=Posts, fixado=fixado,pode_editar=pode_editar, pode_deletar=pode_deletar, canais=getcanais(recuperar_id_usuario_logado()), titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)
        else:
            Posts = []
            return render_template('posts.html', id_canal=id_canal, Posts=Posts, fixado=fixado,pode_editar=pode_editar, pode_deletar=pode_deletar, canais=getcanais(recuperar_id_usuario_logado()), titulocanal=getChannel(id_canal), pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)

    return render_template('posts.html', id_canal= id_canal, pesquisa_postagem = False, fixado=fixado, emails = listar_usuario(), visibilidade_canal = recuperar_visibilidade_canal(id_canal), lista_de_grupos = grupos, lista_de_cursos = cursos)

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
    return render_template('gerenciamento_canal.html', id_canal=id_canal, canais=getcanais(recuperar_id_usuario_logado()), titulocanal = nome_canal,  moderadores = moderadores, participantes = participantes, pode_criar_canal = pode_criar_canais(recuperar_id_usuario_logado()), pode_gerenciar_usuario = pode_gerenciar_usuarios(recuperar_id_usuario_logado()), visibilidade_canal=visibilidade_canal, emails = listar_usuario(), coordenadores_selecionados = coordenadores_selecionados(id_canal), professores_selecionados = professores_selecionados(id_canal), alunos_selecionados = alunos_selecionados(id_canal), lista_cursos = lista_cursos(id_canal))

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

def pode_recuperar_senha():
    if request.cookies.get('changePassword'):
        return True
    else:
        return False

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

#Gerenciamento da visibilidade do canal (Público / Privado) dos grupos(aluno, professor e ou coordenador) e dos cursos
@app.route('/editar_canal', methods = ['POST'])
def editar_canal():
    id_canal = request.args.get('canal')
    visibilidade_canal = request.form.get('visibilidade_canal')
    grupos_canal = request.form.getlist('grupo')
    cursos_canal = request.form.getlist('curso')
    editar_visibilidade(id_canal, visibilidade_canal)
    editar_destinatarios_canal(id_canal, grupos_canal, cursos_canal)
    return redirect(url_for('configuracao_canal', canal=id_canal))
