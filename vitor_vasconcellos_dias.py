import mysql.connector
from mysql.connector import Error

# Conexão com o banco de dados
def criar_conexao():
    try:
        conexao = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",
            database="aplicativo_mensagens"
        )
        print("✅ Conectado ao banco de dados com sucesso!")
        return conexao
    except Error as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

# Cadastro de novo usuário
def cadastrar_usuario(conexao):
    cursor = conexao.cursor()
    nome = input("Nome: ")
    cpf = input("CPF (somente números): ")
    email = input("Email: ")
    senha = input("Senha: ")
    is_admin = input("É administrador? (s/n): ").lower() == 's'

    sql = '''
        INSERT INTO usuarios (nome, cpf, email, senha, is_admin)
        VALUES (%s, %s, %s, %s, %s)
    '''
    valores = (nome, cpf, email, senha, is_admin)

    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Usuário cadastrado com sucesso!")
    except Error as e:
        print(f"Erro ao cadastrar usuário: {e}")

# Login de usuário
def login(conexao):
    cursor = conexao.cursor(dictionary=True)
    email = input("Email: ")
    senha = input("Senha: ")

    sql = "SELECT * FROM usuarios WHERE email = %s AND senha = %s AND ativo = TRUE"
    cursor.execute(sql, (email, senha))
    usuario = cursor.fetchone()

    if usuario:
        print(f"\nBem-vindo, {usuario['nome']}!")
        return usuario
    else:
        print("Email ou senha incorretos, ou conta desativada.")
        return None

# Criação de grupo
def criar_grupo(conexao, usuario_logado):
    cursor = conexao.cursor()
    nome_grupo = input("Nome do grupo: ")

    sql = '''
        INSERT INTO grupos (nome, criador_id)
        VALUES (%s, %s)
    '''
    valores = (nome_grupo, usuario_logado['usuario_id'])

    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Grupo criado com sucesso!")
    except Error as e:
        print(f"Erro ao criar grupo: {e}")

# Adicionar usuário a grupo
def adicionar_usuario_ao_grupo(conexao, usuario_logado):
    cursor = conexao.cursor(dictionary=True)

    try:
        sql = "SELECT * FROM grupos WHERE criador_id = %s AND ativo = TRUE"
        cursor.execute(sql, (usuario_logado['usuario_id'],))
        grupos = cursor.fetchall()

        if not grupos:
            print("Você ainda não criou nenhum grupo.")
            return

        print("\nSeus grupos:")
        for grupo in grupos:
            print(f"{grupo['grupo_id']} - {grupo['nome']}")

        grupo_id = int(input("Digite o ID do grupo que deseja adicionar um usuário: "))
        email_usuario = input("Digite o email do usuário que deseja adicionar: ")

        cursor.execute("SELECT usuario_id, nome FROM usuarios WHERE email = %s AND ativo = TRUE", (email_usuario,))
        usuario = cursor.fetchone()

        if not usuario:
            print("Usuário não encontrado ou está desativado.")
            return

        cursor.execute(
            "SELECT * FROM grupo_usuarios WHERE grupo_id = %s AND usuario_id = %s",
            (grupo_id, usuario['usuario_id'])
        )
        if cursor.fetchone():
            print("Este usuário já está no grupo.")
            return

        sql_insert = "INSERT INTO grupo_usuarios (grupo_id, usuario_id) VALUES (%s, %s)"
        cursor.execute(sql_insert, (grupo_id, usuario['usuario_id']))
        conexao.commit()
        print(f"Usuário {usuario['nome']} adicionado ao grupo com sucesso!")

    except Error as e:
        print(f"Erro ao adicionar usuário ao grupo: {e}")

# Envio de mensagem (privada ou para grupo)
def enviar_mensagem(conexao, usuario_logado):
    cursor = conexao.cursor()
    print("\n1 - Enviar mensagem para um usuário")
    print("2 - Enviar mensagem para um grupo")
    opcao = input("Escolha o tipo de mensagem: ")

    if opcao == "1":
        email_destinatario = input("Email do destinatário: ")
        if email_destinatario == usuario_logado['email']:
            destinatario_id = usuario_logado['usuario_id']
        else:
            cursor.execute("SELECT usuario_id FROM usuarios WHERE email = %s AND ativo = TRUE", (email_destinatario,))
            destinatario = cursor.fetchone()
            if not destinatario:
                print("Usuário não encontrado ou está inativo.")
                return
            destinatario_id = destinatario[0]

        conteudo = input("Digite a mensagem: ")

        sql = '''
            INSERT INTO mensagens (remetente_id, destinatario_id, conteudo)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(sql, (usuario_logado['usuario_id'], destinatario_id, conteudo))
        conexao.commit()
        print("Mensagem enviada com sucesso!")

    elif opcao == "2":
        cursor.execute("SELECT grupo_id, nome FROM grupos WHERE ativo = TRUE")
        grupos = cursor.fetchall()
        if not grupos:
            print("Nenhum grupo disponível.")
            return

        print("\nGrupos disponíveis:")
        for g in grupos:
            print(f"{g[0]} - {g[1]}")
        grupo_id = input("Digite o ID do grupo: ")

        cursor.execute(
            "SELECT * FROM grupo_usuarios WHERE grupo_id = %s AND usuario_id = %s",
            (grupo_id, usuario_logado['usuario_id'])
        )
        if not cursor.fetchone():
            print("Você não faz parte desse grupo.")
            return

        conteudo = input("Digite a mensagem: ")
        sql = '''
            INSERT INTO mensagens (remetente_id, grupo_id, conteudo)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(sql, (usuario_logado['usuario_id'], grupo_id, conteudo))
        conexao.commit()
        print("Mensagem enviada ao grupo com sucesso!")
    else:
        print("Opção inválida.")

# Edição de mensagem enviada
def editar_mensagem(conexao, usuario_logado):
    listar_mensagens_enviadas(conexao, usuario_logado)
    msg_id = input("\nID da mensagem que deseja editar: ")
    novo_conteudo = input("Novo conteúdo: ")

    sql = '''
        UPDATE mensagens
        SET conteudo = %s, data_edicao = NOW()
        WHERE mensagem_id = %s AND remetente_id = %s
    '''
    cursor = conexao.cursor()
    cursor.execute(sql, (novo_conteudo, msg_id, usuario_logado['usuario_id']))
    conexao.commit()

    if cursor.rowcount > 0:
        print("Mensagem editada com sucesso!")
    else:
        print("Mensagem não encontrada ou você não tem permissão para editá-la.")

# Remoção lógica de mensagens (enviadas ou recebidas)
def remover_mensagem(conexao, usuario_logado):
    cursor = conexao.cursor(dictionary=True)
    print("\n1 - Remover mensagem enviada")
    print("2 - Remover mensagem recebida")
    opcao = input("Escolha: ")

    if opcao == "1":
        sql = '''
            SELECT mensagem_id, conteudo FROM mensagens
            WHERE remetente_id = %s AND removida_por_remetente = FALSE
        '''
        cursor.execute(sql, (usuario_logado['usuario_id'],))
    elif opcao == "2":
        sql = '''
            SELECT mensagem_id, conteudo FROM mensagens
            WHERE destinatario_id = %s AND removida_por_destinatario = FALSE
        '''
        cursor.execute(sql, (usuario_logado['usuario_id'],))
    else:
        print("Opção inválida.")
        return

    mensagens = cursor.fetchall()
    if not mensagens:
        print("Nenhuma mensagem disponível para remoção.")
        return

    for msg in mensagens:
        print(f"ID: {msg['mensagem_id']} | Conteúdo: {msg['conteudo']}")

    msg_id = input("Digite o ID da mensagem para remover: ")

    if opcao == "1":
        sql_remover = '''
            UPDATE mensagens
            SET removida_por_remetente = TRUE
            WHERE mensagem_id = %s AND remetente_id = %s
        '''
    else:
        sql_remover = '''
            UPDATE mensagens
            SET removida_por_destinatario = TRUE
            WHERE mensagem_id = %s AND destinatario_id = %s
        '''

    cursor.execute(sql_remover, (msg_id, usuario_logado['usuario_id']))
    conexao.commit()

    if cursor.rowcount > 0:
        print("Mensagem marcada como removida.")
    else:
        print("Não foi possível remover a mensagem.")

# Lista mensagens enviadas pelo usuário logado
def listar_mensagens_enviadas(conexao, usuario_logado):
    cursor = conexao.cursor(dictionary=True)
    sql = '''
        SELECT mensagem_id, conteudo, data_envio, data_edicao, destinatario_id, grupo_id
        FROM mensagens
        WHERE remetente_id = %s AND removida_por_remetente = FALSE
    '''
    cursor.execute(sql, (usuario_logado['usuario_id'],))
    mensagens = cursor.fetchall()

    if not mensagens:
        print("Nenhuma mensagem enviada encontrada.")
        return

    for msg in mensagens:
        tipo = "Grupo" if msg['grupo_id'] else "Privada"
        print(f"\nID: {msg['mensagem_id']} | Tipo: {tipo}")
        print(f"Enviada em: {msg['data_envio']}")
        if msg['data_edicao']:
            print(f"Editada em: {msg['data_edicao']}")
        print(f"Conteúdo: {msg['conteudo']}")

# Lista mensagens recebidas pelo usuário logado
def listar_mensagens_recebidas(conexao, usuario_logado):
    cursor = conexao.cursor(dictionary=True)
    sql = '''
        SELECT m.mensagem_id, m.conteudo, m.data_envio, m.data_edicao,
               u.nome AS remetente_nome,
               g.nome AS grupo_nome
        FROM mensagens m
        LEFT JOIN usuarios u ON m.remetente_id = u.usuario_id
        LEFT JOIN grupos g ON m.grupo_id = g.grupo_id
        WHERE (m.destinatario_id = %s OR m.grupo_id IN (
            SELECT grupo_id FROM grupo_usuarios WHERE usuario_id = %s
        )) AND m.removida_por_destinatario = FALSE
        ORDER BY m.data_envio DESC
    '''
    cursor.execute(sql, (usuario_logado['usuario_id'], usuario_logado['usuario_id']))
    mensagens = cursor.fetchall()

    if not mensagens:
        print("Nenhuma mensagem recebida encontrada.")
        return

    for msg in mensagens:
        remetente = msg['remetente_nome'] if msg['remetente_nome'] else "Desconhecido"
        tipo = f"Grupo: {msg['grupo_nome']}" if msg['grupo_nome'] else "Privada"
        print(f"\nID: {msg['mensagem_id']} | Tipo: {tipo}")
        print(f"De: {remetente}")
        print(f"Enviada em: {msg['data_envio']}")
        if msg['data_edicao']:
            print(f"Editada em: {msg['data_edicao']}")
        print(f"Conteúdo: {msg['conteudo']}")


# Lista mensagens recebidas para o usuário poder denunciar
def listar_mensagens_para_denuncia(conexao, usuario_logado):
    cursor = conexao.cursor(dictionary=True)
    sql = '''
        SELECT m.mensagem_id, m.conteudo, u.nome AS remetente
        FROM mensagens m
        JOIN usuarios u ON m.remetente_id = u.usuario_id
        WHERE (m.destinatario_id = %s OR m.grupo_id IN (
            SELECT grupo_id FROM grupo_usuarios WHERE usuario_id = %s
        )) AND m.removida_por_destinatario = FALSE
    '''
    cursor.execute(sql, (usuario_logado['usuario_id'], usuario_logado['usuario_id']))
    mensagens = cursor.fetchall()

    if not mensagens:
        print("Nenhuma mensagem disponível para denúncia.")
        return []

    for msg in mensagens:
        print(f"\nID: {msg['mensagem_id']} | Remetente: {msg['remetente']}")
        print(f"Conteúdo: {msg['conteudo']}")

    return mensagens

# Permite o usuário denunciar uma mensagem
def denunciar_mensagem(conexao, usuario_logado):
    mensagens = listar_mensagens_para_denuncia(conexao, usuario_logado)
    if not mensagens:
        return

    msg_id = input("\nDigite o ID da mensagem que deseja denunciar: ")
    motivo = input("Motivo da denúncia: ")

    cursor = conexao.cursor()

    # Verifica se é uma mensagem de grupo
    cursor.execute("SELECT grupo_id FROM mensagens WHERE mensagem_id = %s", (msg_id,))
    resultado = cursor.fetchone()
    grupo_id = resultado[0] if resultado else None

    sql = '''
        INSERT INTO denuncias (mensagem_id, grupo_id, denunciante_id, motivo)
        VALUES (%s, %s, %s, %s)
    '''
    valores = (msg_id, grupo_id, usuario_logado['usuario_id'], motivo)

    try:
        cursor.execute(sql, valores)
        conexao.commit()
        print("Denúncia registrada com sucesso!")
    except Error as e:
        print(f"Erro ao registrar denúncia: {e}")

# Exibe todas as denúncias registradas (apenas para admin)
def visualizar_denuncias(conexao):
    cursor = conexao.cursor(dictionary=True)
    sql = '''
        SELECT d.denuncia_id, d.motivo, d.data_denuncia,
               u.nome AS denunciante, m.conteudo AS mensagem_denunciada,
               remetente.nome AS autor_mensagem,
               g.nome AS grupo
        FROM denuncias d
        JOIN usuarios u ON d.denunciante_id = u.usuario_id
        JOIN mensagens m ON d.mensagem_id = m.mensagem_id
        JOIN usuarios remetente ON m.remetente_id = remetente.usuario_id
        LEFT JOIN grupos g ON d.grupo_id = g.grupo_id
        ORDER BY d.data_denuncia DESC
    '''
    cursor.execute(sql)
    denuncias = cursor.fetchall()

    if not denuncias:
        print("Nenhuma denúncia encontrada.")
        return

    print("\nDENÚNCIAS REGISTRADAS:")
    for d in denuncias:
        tipo = f"Grupo: {d['grupo']}" if d['grupo'] else "Privada"
        print(f"\nDenúncia ID: {d['denuncia_id']}")
        print(f"Denunciante: {d['denunciante']}")
        print(f"Autor da Mensagem: {d['autor_mensagem']}")
        print(f"Mensagem: {d['mensagem_denunciada']}")
        print(f"Tipo: {tipo}")
        print(f"Motivo: {d['motivo']}")
        print(f"Data: {d['data_denuncia']}")

# Desativa um usuário a partir do email (admin)
def desativar_usuario(conexao):
    cursor = conexao.cursor()
    email = input("Email do usuário que deseja desativar: ")

    sql = "UPDATE usuarios SET ativo = FALSE WHERE email = %s AND ativo = TRUE"
    cursor.execute(sql, (email,))
    conexao.commit()

    if cursor.rowcount:
        print("Usuário desativado com sucesso.")
    else:
        print("Usuário não encontrado ou já está desativado.")

# Desativa um grupo pelo nome (admin)
def desativar_grupo(conexao):
    cursor = conexao.cursor()
    nome = input("Nome do grupo que deseja desativar: ")

    sql = "UPDATE grupos SET ativo = FALSE WHERE nome = %s AND ativo = TRUE"
    cursor.execute(sql, (nome,))
    conexao.commit()

    if cursor.rowcount:
        print("Grupo desativado com sucesso.")
    else:
        print("Grupo não encontrado ou já está desativado.")

# Relatório: total de mensagens recebidas por usuário
def relatorio_media_mensagens_recebidas(conexao):
    cursor = conexao.cursor()
    print("\nMédia de mensagens recebidas por usuário:")

    sql = """
        SELECT u.nome, COUNT(m.mensagem_id) AS total_recebidas
        FROM usuarios u
        LEFT JOIN mensagens m ON u.usuario_id = m.destinatario_id
        GROUP BY u.usuario_id, u.nome
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    for nome, total in resultados:
        print(f"{nome} recebeu {total} mensagens.")

# Relatório: usuários com mais amigos (membros em grupos diferentes)
def relatorio_usuarios_com_mais_amigos(conexao):
    cursor = conexao.cursor()
    print("\nUsuários com mais amigos:")

    sql = """
        SELECT u.nome, COUNT(DISTINCT gu2.usuario_id) AS amigos
        FROM grupo_usuarios gu1
        JOIN grupo_usuarios gu2 ON gu1.grupo_id = gu2.grupo_id AND gu1.usuario_id <> gu2.usuario_id
        JOIN usuarios u ON u.usuario_id = gu1.usuario_id
        GROUP BY gu1.usuario_id, u.nome
        ORDER BY amigos DESC
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    for nome, qtd_amigos in resultados:
        print(f"{nome} tem {qtd_amigos} amigos.")

# Relatório: quantidade de usuários por grupo
def relatorio_qtd_usuarios_por_grupo(conexao):
    cursor = conexao.cursor()
    print("\nQuantidade de usuários por grupo:")

    sql = """
        SELECT g.nome, COUNT(gu.usuario_id) AS total_usuarios
        FROM grupos g
        LEFT JOIN grupo_usuarios gu ON g.grupo_id = gu.grupo_id
        GROUP BY g.grupo_id, g.nome
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    for grupo, total in resultados:
        print(f"Grupo '{grupo}' tem {total} usuários.")

# Relatório: usuários com mais de 3 denúncias
def relatorio_usuarios_mais_de_3_denuncias(conexao):
    cursor = conexao.cursor()
    print("\nUsuários com mais de 3 denúncias:")

    sql = """
        SELECT u.nome, COUNT(d.denuncia_id) AS total_denuncias
        FROM denuncias d
        JOIN mensagens m ON d.mensagem_id = m.mensagem_id
        JOIN usuarios u ON m.remetente_id = u.usuario_id
        GROUP BY u.usuario_id, u.nome
        HAVING total_denuncias > 3
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    for nome, total in resultados:
        print(f"{nome} foi denunciado {total} vezes.")

# Relatório: motivos mais comuns de denúncia
def relatorio_motivos_comuns_denuncia(conexao):
    cursor = conexao.cursor()
    print("\nMotivos mais comuns de denúncia:")

    sql = """
        SELECT motivo, COUNT(*) AS ocorrencias
        FROM denuncias
        GROUP BY motivo
        ORDER BY ocorrencias DESC
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    for motivo, qtd in resultados:
        print(f"Motivo: '{motivo}' — {qtd} ocorrência(s)")

# Relatório: usuários que participam de mais grupos
def relatorio_usuarios_em_mais_grupos(conexao):
    cursor = conexao.cursor()
    print("\nUsuários que participam de mais grupos:")

    sql = """
        SELECT u.nome, COUNT(gu.grupo_id) AS total_grupos
        FROM usuarios u
        JOIN grupo_usuarios gu ON u.usuario_id = gu.usuario_id
        GROUP BY u.usuario_id, u.nome
        ORDER BY total_grupos DESC, u.nome ASC
    """
    cursor.execute(sql)
    resultados = cursor.fetchall()

    for nome, qtd in resultados:
        print(f"{nome} participa de {qtd} grupo(s).")

# Relatório: usuário há mais tempo sem enviar mensagem
def relatorio_usuario_sem_mensagens(conexao):
    cursor = conexao.cursor()
    print("\nUsuário há mais tempo sem enviar mensagens:")

    sql = """
        SELECT u.nome, MAX(m.data_envio) AS ultima_mensagem
        FROM usuarios u
        LEFT JOIN mensagens m ON u.usuario_id = m.remetente_id
        GROUP BY u.usuario_id
        ORDER BY ultima_mensagem ASC
        LIMIT 1
    """
    cursor.execute(sql)
    resultado = cursor.fetchone()

    if resultado:
        nome, ultima_data = resultado
        data_info = ultima_data if ultima_data else "Nunca enviou mensagem"
        print(f"{nome} — Última mensagem: {data_info}")
    else:
        print("Nenhum usuário encontrado.")

# Exclui mensagens removidas por remetente e destinatário
def excluir_mensagens_removidas(conexao):
    cursor = conexao.cursor()
    print("\nLimpando mensagens removidas...")

    sql = """
        DELETE FROM mensagens
        WHERE removida_por_remetente = TRUE
        AND removida_por_destinatario = TRUE
    """
    cursor.execute(sql)
    conexao.commit()

    print(f"{cursor.rowcount} mensagem(ns) excluída(s) do sistema.")

# Relatório: mensagens enviadas e recebidas por período e usuário
def relatorio_mensagens_por_periodo(conexao):
    cursor = conexao.cursor()

    email = input("Email do usuário (digite 0 para voltar): ")
    if email == '0':
        return
    
    data_inicio = input("Data de início (YYYY-MM-DD) (digite 0 para voltar): ")
    if data_inicio == '0':
        return
    
    data_fim = input("Data de fim (YYYY-MM-DD) (digite 0 para voltar): ")
    if data_fim == '0':
        return

    cursor.execute("SELECT usuario_id, nome FROM usuarios WHERE email = %s", (email,))
    usuario = cursor.fetchone()
    if not usuario:
        print("Usuário não encontrado.")
        return

    usuario_id, nome = usuario

    sql_env = """
        SELECT COUNT(*) FROM mensagens
        WHERE remetente_id = %s AND data_envio BETWEEN %s AND %s
    """
    sql_rec = """
        SELECT COUNT(*) FROM mensagens
        WHERE destinatario_id = %s AND data_envio BETWEEN %s AND %s
    """

    cursor.execute(sql_env, (usuario_id, data_inicio, data_fim))
    enviadas = cursor.fetchone()[0]

    cursor.execute(sql_rec, (usuario_id, data_inicio, data_fim))
    recebidas = cursor.fetchone()[0]

    print(f"\n{nome} enviou {enviadas} e recebeu {recebidas} mensagem(ns) entre {data_inicio} e {data_fim}.")

# Envia a mesma mensagem para vários grupos
def enviar_para_varios_grupos(conexao, usuario_logado):
    cursor = conexao.cursor()
    cursor.execute("""
        SELECT g.grupo_id, g.nome
        FROM grupos g
        JOIN grupo_usuarios gu ON g.grupo_id = gu.grupo_id
        WHERE gu.usuario_id = %s AND g.ativo = TRUE
    """, (usuario_logado['usuario_id'],))
    grupos = cursor.fetchall()

    if not grupos:
        print("Você não participa de nenhum grupo.")
        return

    print("\nSeus grupos disponíveis:")
    for g in grupos:
        print(f"{g[0]} - {g[1]}")

    ids = input("Digite os IDs dos grupos separados por vírgula (ex: 1,3,5): ")
    try:
        ids_selecionados = [int(x.strip()) for x in ids.split(",") if x.strip().isdigit()]
    except:
        print("IDs inválidos.")
        return

    conteudo = input("Digite a mensagem para enviar aos grupos selecionados: ")

    sql = '''
        INSERT INTO mensagens (remetente_id, grupo_id, conteudo)
        VALUES (%s, %s, %s)
    '''

    count = 0
    for grupo_id in ids_selecionados:
        cursor.execute(sql, (usuario_logado['usuario_id'], grupo_id, conteudo))
        count += 1

    conexao.commit()
    print(f"Mensagem enviada para {count} grupo(s) com sucesso!")

# Menu do usuário e administrador
def menu_usuario(conexao, usuario_logado):
    while True:
        print("\n====== MENU DO USUÁRIO ======")
        print("1 - Criar grupo")
        print("2 - Adicionar usuário a grupo")
        print("3 - Enviar mensagem")
        print("4 - Editar mensagem")
        print("5 - Remover mensagem")
        print("6 - Denunciar mensagem")
        print("7 - Enviar a mesma mensagem para vários grupos")
        print("8 - Ver mensagens recebidas")
        if usuario_logado.get("is_admin", False):
            print("9 - Visualizar denúncias")
            print("10 - Desativar usuário")
            print("11 - Desativar grupo")
            print("12 - Relatórios avançados")
        print("0 - Sair da conta")

        opcao_usuario = input("Escolha uma opção: ")

        if opcao_usuario == "1":
            criar_grupo(conexao, usuario_logado)
        elif opcao_usuario == "2":
            adicionar_usuario_ao_grupo(conexao, usuario_logado)
        elif opcao_usuario == "3":
            enviar_mensagem(conexao, usuario_logado)
        elif opcao_usuario == "4":
            editar_mensagem(conexao, usuario_logado)
        elif opcao_usuario == "5":
            remover_mensagem(conexao, usuario_logado)
        elif opcao_usuario == "6":
            denunciar_mensagem(conexao, usuario_logado)
        elif opcao_usuario == "7":
            enviar_para_varios_grupos(conexao, usuario_logado)
        elif opcao_usuario == "8":
            listar_mensagens_recebidas(conexao, usuario_logado)
        elif opcao_usuario == "9" and usuario_logado.get("is_admin", False):
            visualizar_denuncias(conexao)
        elif opcao_usuario == "10" and usuario_logado.get("is_admin", False):
            desativar_usuario(conexao)
        elif opcao_usuario == "11" and usuario_logado.get("is_admin", False):
            desativar_grupo(conexao)
        elif opcao_usuario == "12" and usuario_logado.get("is_admin", False):
            # Chama os relatórios implementados
            relatorio_usuarios_com_mais_amigos(conexao)
            relatorio_qtd_usuarios_por_grupo(conexao)
            relatorio_usuarios_mais_de_3_denuncias(conexao)
            relatorio_motivos_comuns_denuncia(conexao)
            relatorio_usuarios_em_mais_grupos(conexao)
            relatorio_usuario_sem_mensagens(conexao)
            excluir_mensagens_removidas(conexao)
            relatorio_mensagens_por_periodo(conexao)
        elif opcao_usuario == "0":
            print("Logout realizado.")
            break
        else:
            print("Opção inválida.")

# Menu inicial
def main():
    conexao = criar_conexao()
    if not conexao:
        return

    while True:
        print("\n====== MENU INICIAL ======")
        print("1 - Cadastrar usuário")
        print("2 - Login")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_usuario(conexao)
        elif opcao == "2":
            usuario = login(conexao)
            if usuario:
                menu_usuario(conexao, usuario)
        elif opcao == "0":
            print("Encerrando programa.")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
