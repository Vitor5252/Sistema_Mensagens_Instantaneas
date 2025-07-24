CREATE DATABASE aplicativo_mensagens;
USE aplicativo_mensagens;

CREATE TABLE usuarios (
    usuario_id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    cpf CHAR(11) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(100) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    ativo BOOLEAN DEFAULT TRUE
);

CREATE TABLE grupos (
    grupo_id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    criador_id INT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (criador_id) REFERENCES usuarios(usuario_id)
);

CREATE TABLE grupo_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    grupo_id INT NOT NULL,
    usuario_id INT NOT NULL,
    FOREIGN KEY (grupo_id) REFERENCES grupos(grupo_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(usuario_id)
);

CREATE TABLE mensagens (
    mensagem_id INT AUTO_INCREMENT PRIMARY KEY,
    remetente_id INT NOT NULL,
    destinatario_id INT,
    grupo_id INT,
    conteudo TEXT NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    data_edicao DATETIME,
    removida_por_remetente BOOLEAN DEFAULT FALSE,
    removida_por_destinatario BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (remetente_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (destinatario_id) REFERENCES usuarios(usuario_id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(grupo_id)
);

CREATE TABLE denuncias (
    denuncia_id INT AUTO_INCREMENT PRIMARY KEY,
    mensagem_id INT,
    grupo_id INT,
    denunciante_id INT NOT NULL,
    motivo TEXT NOT NULL,
    data_denuncia DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (mensagem_id) REFERENCES mensagens(mensagem_id),
    FOREIGN KEY (grupo_id) REFERENCES grupos(grupo_id),
    FOREIGN KEY (denunciante_id) REFERENCES usuarios(usuario_id)
);

-- Inserção de usuários (incluindo admin e comuns)
INSERT INTO usuarios (nome, cpf, email, senha, is_admin, ativo) VALUES
('Vitor Vasconcellos', '12345678900', 'vitor@email.com', '1234', TRUE, TRUE),
('João Brandão', '11122233344', 'joao@email.com', 'abcd', FALSE, TRUE),
('Henrique Brasil', '55566677788', 'henrique@email.com', 'henrique123', FALSE, TRUE),
('Kalebe dos Santos', '99988877766', 'kalebe@email.com', 'kalebe321', FALSE, TRUE),
('Clara Ribeiro', '22233344455', 'clara@email.com', 'clara123', FALSE, TRUE),
('Isadora Fernandes', '77766655544', 'isadora@email.com', 'isa123', FALSE, TRUE);

-- Inserção de grupos
INSERT INTO grupos (nome, criador_id, ativo) VALUES
('Grupo Trabalho', 1, TRUE),
('Grupo Amigos', 2, TRUE),
('Grupo Faculdade', 3, TRUE);

-- Inserção de usuários em grupos
INSERT INTO grupo_usuarios (grupo_id, usuario_id) VALUES
(1, 1), (1, 2), (1, 4), (1, 5),
(2, 2), (2, 3), (2, 4), (2, 6),
(3, 3), (3, 4), (3, 1), (3, 5), (3, 6);

-- Inserção de mensagens diretas
INSERT INTO mensagens (remetente_id, destinatario_id, conteudo) VALUES
(1, 2, 'Bom dia, João! Como está o projeto?'),
(2, 1, 'Oi Vitor, está quase pronto.'),
(3, 4, 'Oi Kalebe, quer estudar hoje?'),
(4, 3, 'Sim! Mais tarde?'),
(5, 6, 'Isa, vai na aula hoje?'),
(6, 5, 'Vou sim, Clara. Avisa a prof!');

-- Inserção de mensagens em grupo
INSERT INTO mensagens (remetente_id, grupo_id, conteudo) VALUES
(1, 1, 'Reunião hoje às 18h.'),
(2, 1, 'Confirmado!'),
(3, 3, 'Trabalho de BD para sexta!'),
(4, 3, 'Vou revisar os tópicos.'),
(2, 2, 'Bora sair sábado?'),
(5, 3, 'Alguém terminou o relatório?'),
(6, 3, 'Estou terminando agora.');

-- Inserção de denúncias
INSERT INTO denuncias (mensagem_id, grupo_id, denunciante_id, motivo) VALUES
(5, 1, 1, 'Spam'),
(6, 1, 2, 'Mensagem repetida'),
(7, 3, 4, 'Informação falsa'),
(8, 3, 3, 'Ofensiva'),
(9, 2, 1, 'Inadequada'),
(10, 3, 6, 'Piada ofensiva');

