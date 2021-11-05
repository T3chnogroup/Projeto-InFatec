def insertUser(cur, mysql, nome, email, senha, cpf):
  if cur.execute("INSERT INTO usuario(id_usuario, nome, email, senha, cpf, valido, pode_gerenciar_usuario, pode_criar_canais) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (0, nome, email, senha, cpf, 0, 0, 0)):
    mysql.connection.commit()
    cur.close()
    return True
  else:
    return False

def registeredEmail(cursor, mysql, email):
  cursor.execute("SELECT email FROM usuario where email = %s", (email,))
  if cursor.rowcount > 0:
    return True
  else:
    return False;

def registeredCpf(cursor, mysql, cpf):
  cursor.execute("SELECT cpf FROM usuario where cpf = %s", (cpf,))
  if cursor.rowcount > 0:
    return True
  else:
    return False;
