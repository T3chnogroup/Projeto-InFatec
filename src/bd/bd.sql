DROP DATABASE IF EXISTS infatec;
CREATE DATABASE infatec;
USE infatec;

CREATE TABLE IF NOT EXISTS usuario (
	id_usuario INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	email VARCHAR(100) NOT NULL,
	senha VARCHAR(15) NOT NULL,
	cpf CHAR(11) NOT NULL
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS canal (
	id_canal INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(30) NOT NULL,
	grupo INT,
	semestre INT,
	curso INT,
	fk_usuario INT,
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS post (
	id_post INT AUTO_INCREMENT PRIMARY KEY,
	data_postagem DATE NOT NULL,
	data_expiracao DATE NOT NULL,
	conteudo TEXT NOT NULL,
	fk_canal INT,
	fk_usuario INT,
	FOREIGN KEY (fk_canal) REFERENCES canal (id_canal),
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS anexo (
	id_anexo INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(30) NOT NULL,
	fk_post INT,
	FOREIGN KEY (fk_post) REFERENCES post (id_post)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS visualizado_por (
	fk_usuario INT,
	fk_post INT,
	data_visualizacao DATE,
	PRIMARY KEY (fk_usuario, fk_post),
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario),
	FOREIGN KEY (fk_post) REFERENCES post (id_post)
);

CREATE TABLE IF NOT EXISTS usuario_canal (
	fk_usuario INT,
	fk_canal INT,
	PRIMARY KEY (fk_usuario, fk_canal),
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario),
	FOREIGN KEY (fk_canal) REFERENCES canal (id_canal)
);

-- Inserção tabela usuario
INSERT INTO usuario VALUES (0, "Lucas", "lucasbrzdias@gmail.com", "123456", "33333333333");

-- Consulta todos os
select * from usuario;

-- Inserção tabela canal
INSERT INTO canal(nome, grupo, semestre, curso) VALUES ("geral", null, null, null);
select * from canal;

-- Inserção tabela post
INSERT INTO post VALUES (0, "2021-10-08", "2021-10-12", "Conteudo legal", 1, 1);
INSERT INTO post VALUES (0, "2021-10-08", "2021-10-12", "Conteudo chato", 1, 1);
select * from post;
