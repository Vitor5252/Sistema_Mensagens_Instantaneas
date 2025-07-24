💬 Sistema de Mensagens Instantâneas
Projeto desenvolvido para simular um aplicativo de mensagens com foco em segurança, rastreabilidade e controle administrativo, utilizando Python e MySQL. O sistema garante que cada usuário possua apenas uma conta, utilizando o CPF como identificador único, visando combater perfis falsos e promover interações mais confiáveis.

🎯 Objetivo
Criar uma plataforma de mensagens onde usuários podem se comunicar por meio de mensagens privadas ou em grupos, com funcionalidades de denúncia, edição, exclusão lógica e envio múltiplo. O sistema também fornece relatórios administrativos para controle e análise das interações.

🧱 Tecnologias Utilizadas
Python 3

MySQL

Conector MySQL para Python (mysql-connector-python)

🧩 Funcionalidades
Cadastro de usuários (comuns e administradores)

Criação e gerenciamento de grupos

Envio de mensagens privadas, para grupos e para si mesmo

Edição e exclusão lógica de mensagens

Envio simultâneo de uma mensagem para múltiplos grupos

Registro e visualização de denúncias

Desativação de contas e grupos (admin)

Relatórios estatísticos e analíticos

🗂️ Organização do Projeto
vitor_vasconcellos_dias.py → código principal em Python

vitor_vasconcellos_dias.sql → estrutura do banco de dados e dados populados

Mensagens_Instantaneas.pdf → especificação completa do sistema

vitor-vasconcellos-dias-diagrama.png → diagrama ER (entidade-relacionamento)

📌 Requisitos
Python 3 instalado

MySQL em execução local (user=root, senha=123456789)

Executar o script SQL antes de rodar o programa
