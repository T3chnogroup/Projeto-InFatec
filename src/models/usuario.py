def insertUser(cur, mysql, nome, email, senha, cpf):
  if cur.execute("INSERT INTO usuario(id_usuario, nome, email, senha, cpf, valido) VALUES (%s, %s, %s, %s, %s, %s)", (0, nome, email, senha, cpf, 0)):
    mysql.connection.commit()
    cur.close()
    return True
  else:
    return False 