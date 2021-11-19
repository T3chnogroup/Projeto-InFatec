def insertUser(cur, mysql, nome, email, senha, cpf):
  if cur.execute("INSERT INTO usuario(id_usuario, nome, email, senha, cpf, valido, pode_gerenciar_usuario, pode_criar_canais) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (0, nome, email, senha, cpf, 0, 0, 0)):
    mysql.connection.commit()
    return True
  else:
    return False

def registeredEmail(cursor, mysql, email):
  cursor.execute("SELECT email FROM usuario where email = %s", (email,))
  if cursor.rowcount > 0:
    return True
  else:
    return False

def registeredCpf(cursor, mysql, cpf):
  cursor.execute("SELECT cpf FROM usuario where cpf = %s", (cpf,))
  if cursor.rowcount > 0:
    return True
  else:
    return False

def validUser(cursor, id_usuario):
  cursor.execute("SELECT valido FROM usuario where id_usuario = %s and valido = 1", (id_usuario,))
  if cursor.rowcount > 0:
    return True
  else:
    return False

def validateUser(cursor, mysql, id_usuario):
    cursor.execute('update usuario set valido = %s where id_usuario = %s', (1, id_usuario))
    mysql.connection.commit()
    cursor.close()

def searchUserByCpf(cursor, cpf):
  cursor.execute("SELECT id_usuario FROM usuario where cpf = %s", (cpf,))
  user = cursor.fetchone()
  return user

def sendConfirmationEmail(message, mail, recipient, confirmationLink):
  msg = message('Email de confirmação', sender = 'Grupo3fatec', recipients = [recipient])
  msg.body = f'Confirme o seu cadastro: {confirmationLink}'
  mail.send(msg)
  return 'Email enviado'