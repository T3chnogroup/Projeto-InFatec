from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

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