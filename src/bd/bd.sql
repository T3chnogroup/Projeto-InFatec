DROP DATABASE IF EXISTS infatec;
CREATE DATABASE infatec;
USE infatec;

CREATE TABLE IF NOT EXISTS usuario (
	id_usuario INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(100) NOT NULL,
	email VARCHAR(100) UNIQUE NOT NULL,
	senha VARCHAR(40) NOT NULL,
	cpf CHAR(11) UNIQUE NOT NULL,
	valido boolean,
	pode_gerenciar_usuario boolean,
	pode_criar_canais boolean
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS canal (
	id_canal INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(30) NOT NULL,
	fk_usuario INT,
	visibilidade varchar(30),
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS post (
	id_post INT AUTO_INCREMENT PRIMARY KEY,
	data_postagem DATE NOT NULL,
	data_expiracao DATE NOT NULL,
	conteudo TEXT NOT NULL,
	fk_canal INT,
	fk_usuario INT,
	titulo_post varchar(100) NOT NULL,
	FOREIGN KEY (fk_canal) REFERENCES canal (id_canal),
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS anexo (
	id_anexo INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(30) NOT NULL,
	fk_post INT,
	FOREIGN KEY (fk_post) REFERENCES post (id_post) ON DELETE CASCADE 
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS visualizado_por (
	fk_usuario INT,
	fk_post INT,
	data_visualizacao DATE,
	PRIMARY KEY (fk_usuario, fk_post),
	FOREIGN KEY (fk_usuario) REFERENCES usuario (id_usuario),
	FOREIGN KEY (fk_post) REFERENCES post (id_post)
);

CREATE TABLE IF NOT EXISTS canal_usuario (
	id_canal INT,
	id_usuario INT,
  funcao varchar(30),
	PRIMARY KEY(id_canal, id_usuario),
    FOREIGN KEY (id_canal) REFERENCES canal (id_canal),
    FOREIGN KEY (id_usuario) REFERENCES usuario (id_usuario)
);

CREATE TABLE IF NOT EXISTS canal_grupo (
	id_canal INT,
	id_grupo INT,
    FOREIGN KEY(id_canal) REFERENCES canal (id_canal),
    PRIMARY KEY (id_canal, id_grupo)
) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS canal_curso (
	id_canal INT,
	nome_curso VARCHAR (100),
    FOREIGN KEY(id_canal) REFERENCES canal (id_canal),
    PRIMARY KEY (id_canal, nome_curso)
) ENGINE=INNODB;

-- Inserção tabela usuario
delete from canal_usuario where id_usuario >=0;
Delete from usuario where id_usuario >=0; 
INSERT INTO usuario VALUES (1, 'Administrador', 'administrador@fatec.sp.gov.br', 'f865b53623b121fd34ee5426c792e5c33af8c227', '88888888888', 1, 1, 1),
(2, "Elen", "elen.petri@fatec.sp.gov.br", "7c4a8d09ca3762af61e59520943dc26494f8941b", "22222222222", 1, 0, 0),
(3, "Tais", "tais.salomao@fatec.sp.gov.br", "7c4a8d09ca3762af61e59520943dc26494f8941b", "33333333332", 1, 0, 0),
(4, "Kevin", "kevin.mirenda@fatec.sp.gov.br", "7c4a8d09ca3762af61e59520943dc26494f8941b", "44444444444", 1, 0, 0),
(5, "Rodrigo", "rodrigo.paula15@fatec.sp.gov.br", "7c4a8d09ca3762af61e59520943dc26494f8941b", "66666666666", 1, 0, 0),
(6, "Priscila", "priscila.silva140@fatec.sp.gov.br", "7c4a8d09ca3762af61e59520943dc26494f8941b", "77777777777", 1, 0, 0);

-- Inserção tabela canal
INSERT INTO canal VALUES (0, "geral", null, null);

-- Inserção tabela post
INSERT INTO post VALUES (0, "2021-10-08", "2021-10-12", "Conteudo legal", 1, 2, "titulo legal"),
(0, "2021-10-08", "2021-10-12", "Conteudo chato", 1, 2, "titulo chato"),
(0, "2021-10-09", "2021-10-12", "Conteudo normal", 1, 2, "titulo normal"),
(0, "2021-10-10", "2021-10-12", "Conteudo anormal", 1, 2, "Conteudo anormal");