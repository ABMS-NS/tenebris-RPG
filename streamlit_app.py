"""
===========================================
SISTEMA DE LOGIN TENEBRIS RPG
===========================================

Este sistema implementa um portal de login/cadastro para o RPG Tenebris,
utilizando GitHub como banco de dados e Streamlit como interface web.

Funcionalidades:
- Login de usuários existentes
- Cadastro de novos usuários com ID automático
- Autenticação com validação
- Persistência de dados no GitHub
- Interface web responsiva

Autor: Sistema Tenebris RPG
Data: 2025
"""

# ===== IMPORTAÇÕES =====
import streamlit as st      # Framework web para criar interfaces interativas
import requests            # Biblioteca para fazer requisições HTTP ao GitHub API
import base64             # Biblioteca para codificar/decodificar arquivos em base64
import json               # Biblioteca para manipular dados JSON

# ===== CONFIGURAÇÕES GLOBAIS =====

# Configurações essenciais para conexão com o repositório GitHub
# que serve como banco de dados do sistema.

REPO = "ABMS-NS/tenebris-RPG"        # Nome do repositório GitHub no formato usuário/repositório
ARQUIVO_JSON = "usuarios.json"        # Nome do arquivo JSON que armazena os dados dos usuários
BRANCH = "main"                       # Branch principal do repositório onde estão os arquivos
TOKEN = st.secrets["GITHUB_TOKEN"]    # Token de acesso ao GitHub armazenado nos secrets do Streamlit

# ===== FUNÇÃO: CARREGAR LISTA DE USUÁRIOS =====
def carregar_usuarios():
    """
    Carrega a lista de usuários do arquivo JSON hospedado no GitHub.
    
    Processo:
    1. Monta a URL da API do GitHub para acessar o arquivo
    2. Configura os headers de autenticação
    3. Faz a requisição HTTP GET
    4. Decodifica o conteúdo base64 retornado
    5. Converte de JSON para objeto Python
    
    Returns:
        list: Lista de dicionários contendo os dados dos usuários
        
    Raises:
        SystemExit: Para a execução se não conseguir carregar o arquivo
    """
    # Monta a URL da API do GitHub para acessar o arquivo específico
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO_JSON}?ref={BRANCH}"
    
    # Configura os headers necessários para autenticação na API do GitHub
    headers = {
        "Authorization": f"token {TOKEN}",      # Token de autenticação
        "Accept": "application/vnd.github.v3+json"  # Especifica a versão da API
    }

    # Faz a requisição HTTP GET para obter o arquivo
    response = requests.get(url, headers=headers)

    # Verifica se a requisição foi bem-sucedida (código 200)
    if response.status_code == 200:
        # Extrai o conteúdo em base64 da resposta JSON
        conteudo_base64 = response.json()["content"]
        # Decodifica o base64 para string
        conteudo = base64.b64decode(conteudo_base64).decode()
        # Converte a string JSON para objeto Python
        return json.loads(conteudo)
    else:
        # Exibe erro e para a execução se não conseguir carregar
        st.error("❌ Não foi possível carregar o banco de dados.")
        st.stop()

# ===== FUNÇÃO: VERIFICAR LOGIN =====
def verificar_login(usuario, senha, usuarios):
    """
    Verifica se as credenciais de login são válidas.
    
    Percorre a lista de usuários e compara o nome de usuário e senha
    fornecidos com os dados armazenados.
    
    Args:
        usuario (str): Nome de usuário fornecido
        senha (str): Senha fornecida
        usuarios (list): Lista de usuários carregada do GitHub
        
    Returns:
        bool: True se as credenciais forem válidas, False caso contrário
    """
    # Percorre todos os usuários na lista
    for u in usuarios:
        # Verifica se o usuário e senha coincidem
        if u["usuario"] == usuario and u["senha"] == senha:
            return True  # Login válido
    return False  # Login inválido

# ===== FUNÇÃO: SALVAR USUÁRIOS NO GITHUB =====
def salvar_usuarios(usuarios):
    """
    Salva a lista atualizada de usuários no arquivo JSON do GitHub.
    
    Processo:
    1. Obtém o SHA atual do arquivo (necessário para atualização)
    2. Converte a lista de usuários para JSON
    3. Codifica em base64
    4. Faz commit da atualização no GitHub
    
    Args:
        usuarios (list): Lista atualizada de usuários
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    # URL da API para acessar/modificar o arquivo
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO_JSON}"
    
    # Headers de autenticação
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Primeiro, precisa obter o SHA atual do arquivo
    # (GitHub exige o SHA para fazer atualizações)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha_atual = response.json()["sha"]  # Extrai o SHA atual
    else:
        st.error("❌ Erro ao acessar o arquivo no GitHub.")
        return False
    
    # Debug: Mostra os dados que serão salvos
    print(f"Debug: Dados que serão salvos: {usuarios}")
    
    # Converte a lista de usuários para string JSON formatada
    # ensure_ascii=False permite caracteres especiais
    # indent=2 formata o JSON de forma legível
    conteudo_json = json.dumps(usuarios, indent=2, ensure_ascii=False)
    
    # Debug: Mostra o JSON que será enviado
    print(f"Debug: JSON gerado: {conteudo_json}")
    
    # Codifica em base64 (formato exigido pela API do GitHub)
    conteudo_base64 = base64.b64encode(conteudo_json.encode('utf-8')).decode('utf-8')
    
    # Prepara os dados para o commit
    dados = {
        "message": "Novo usuário cadastrado",  # Mensagem do commit
        "content": conteudo_base64,           # Conteúdo em base64
        "sha": sha_atual,                     # SHA atual do arquivo
        "branch": BRANCH                      # Branch onde fazer o commit
    }
    
    # Faz o commit (PUT request)
    response = requests.put(url, headers=headers, json=dados)
    
    # Debug: Mostra o resultado da operação
    print(f"Debug: Status da resposta: {response.status_code}")
    if response.status_code != 200:
        print(f"Debug: Erro na resposta: {response.text}")
    
    return response.status_code == 200  # Retorna True se sucesso (código 200)

# ===== FUNÇÃO: VERIFICAR SE USUÁRIO JÁ EXISTE =====
def usuario_existe(usuario, usuarios):
    """
    Verifica se um nome de usuário já está em uso.
    
    Args:
        usuario (str): Nome de usuário a ser verificado
        usuarios (list): Lista de usuários existentes
        
    Returns:
        bool: True se o usuário já existe, False caso contrário
    """
    # Percorre a lista de usuários
    for u in usuarios:
        # Verifica se o nome de usuário já existe
        if u["usuario"] == usuario:
            return True  # Usuário já existe
    return False  # Usuário não existe

# ===== FUNÇÃO: OBTER PRÓXIMO ID =====
def obter_proximo_id(usuarios):
    """
    Calcula o próximo ID disponível para um novo usuário.
    
    Percorre todos os usuários existentes e encontra o maior ID,
    então retorna o próximo número sequencial.
    
    Args:
        usuarios (list): Lista de usuários existentes
        
    Returns:
        int: Próximo ID disponível
    """
    if not usuarios:  # Se não há usuários, começa com ID 1
        return 1
    
    # Lista para armazenar todos os IDs encontrados
    ids_existentes = []
    
    # Percorre todos os usuários e coleta os IDs
    for u in usuarios:
        # Verifica se o usuário tem campo 'id'
        if 'id' in u and isinstance(u['id'], int):
            ids_existentes.append(u['id'])
    
    # Se não há IDs existentes, começa com 1
    if not ids_existentes:
        return 1
    
    # Retorna o maior ID + 1
    return max(ids_existentes) + 1

# ===== FUNÇÃO: CADASTRAR NOVO USUÁRIO =====
def cadastrar_usuario(usuario, senha, usuarios):
    """
    Cadastra um novo usuário no sistema.
    
    Processo:
    1. Verifica se o usuário já existe
    2. Gera um novo ID automático
    3. Cria o objeto do novo usuário
    4. Adiciona à lista de usuários
    5. Salva no GitHub
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha do usuário
        usuarios (list): Lista atual de usuários
        
    Returns:
        tuple: (sucesso, mensagem)
            sucesso (bool): True se cadastrou com sucesso
            mensagem (str): Mensagem de feedback
    """
    # Verifica se o usuário já existe
    if usuario_existe(usuario, usuarios):
        return False, "Usuário já existe."
    
    # Gera o próximo ID disponível
    novo_id = obter_proximo_id(usuarios)
    
    # Cria o objeto do novo usuário com ID, usuário e senha
    novo_usuario = {
        "id": novo_id,
        "usuario": usuario,
        "senha": senha
    }
    
    # Debug: Mostra o novo usuário que será adicionado
    print(f"Debug: Novo usuário criado: {novo_usuario}")
    
    # Adiciona o novo usuário à lista
    usuarios.append(novo_usuario)
    
    # Debug: Mostra a lista completa antes de salvar
    print(f"Debug: Lista de usuários antes de salvar: {usuarios}")
    
    # Tenta salvar no GitHub
    if salvar_usuarios(usuarios):
        return True, f"Usuário cadastrado com sucesso! ID: {novo_id}"
    else:
        return False, "Erro ao salvar usuário."

# ===== FUNÇÃO: PÁGINA DE LOGIN =====
def pagina_login():
    """
    Renderiza a página de login/cadastro.
    
    Cria uma interface com duas abas:
    1. Aba de Login - para usuários existentes
    2. Aba de Cadastro - para novos usuários
    
    Inclui validações de campos e feedback visual.
    """
    # Título principal da página
    st.title("🌒 Login - Tenebris RPG")
    
    # Cria duas abas: Login e Cadastro
    tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])
    
    # === ABA DE LOGIN ===
    with tab1:
        st.subheader("Fazer Login")
        
        # Campos de entrada para login
        usuario_login = st.text_input("Usuário", key="login_usuario")
        senha_login = st.text_input("Senha", type="password", key="login_senha")

        # Botão de login
        if st.button("Entrar", key="btn_login"):
            # Verifica se os campos estão preenchidos
            if usuario_login and senha_login:
                # Carrega a lista de usuários do GitHub
                usuarios = carregar_usuarios()
                
                # Verifica as credenciais
                if verificar_login(usuario_login, senha_login, usuarios):
                    # Login bem-sucedido - atualiza o estado da sessão
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = usuario_login
                    # Recarrega a página para mostrar a área logada
                    st.rerun()
                else:
                    # Credenciais inválidas
                    st.error("Usuário ou senha inválidos.")
            else:
                # Campos em branco
                st.warning("Por favor, preencha todos os campos.")
    
    # === ABA DE CADASTRO ===
    with tab2:
        st.subheader("Cadastrar Novo Usuário")
        
        # Campos de entrada para cadastro
        usuario_cadastro = st.text_input("Novo Usuário", key="cadastro_usuario")
        senha_cadastro = st.text_input("Nova Senha", type="password", key="cadastro_senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", key="confirmar_senha")

        # Botão de cadastro
        if st.button("Cadastrar", key="btn_cadastro"):
            # Verifica se todos os campos estão preenchidos
            if usuario_cadastro and senha_cadastro and confirmar_senha:
                # Verifica se as senhas coincidem
                if senha_cadastro == confirmar_senha:
                    # Verifica critérios mínimos de segurança
                    if len(usuario_cadastro) >= 3 and len(senha_cadastro) >= 4:
                        # Carrega lista atual de usuários
                        usuarios = carregar_usuarios()
                        
                        # Tenta cadastrar o novo usuário
                        sucesso, mensagem = cadastrar_usuario(usuario_cadastro, senha_cadastro, usuarios)
                        
                        if sucesso:
                            # Cadastro bem-sucedido
                            st.success(mensagem)
                            st.info("Agora você pode fazer login com suas credenciais.")
                        else:
                            # Erro no cadastro
                            st.error(mensagem)
                    else:
                        # Critérios mínimos não atendidos
                        st.error("Usuário deve ter pelo menos 3 caracteres e senha pelo menos 4 caracteres.")
                else:
                    # Senhas não coincidem
                    st.error("As senhas não coincidem.")
            else:
                # Campos em branco
                st.warning("Por favor, preencha todos os campos.")


# ===== FUNÇÃO: CARREGAR LISTA DE MESAS =====
def carregar_mesas():
    """
    Carrega a lista de todas as mesas disponíveis na pasta 'mesas' do GitHub.
    
    Returns:
        list: Lista de dicionários contendo os dados das mesas
    """
    # URL da API para acessar a pasta mesas
    url = f"https://api.github.com/repos/{REPO}/contents/mesas?ref={BRANCH}"
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        arquivos = response.json()
        mesas = []
        
        # Filtra apenas arquivos JSON
        for arquivo in arquivos:
            if arquivo["name"].endswith(".json"):
                # Carrega o conteúdo de cada mesa
                mesa_data = carregar_mesa_individual(arquivo["name"])
                if mesa_data:
                    mesas.append(mesa_data)
        
        return mesas
    else:
        st.error("❌ Não foi possível carregar a lista de mesas.")
        return []

# ===== FUNÇÃO: CARREGAR MESA INDIVIDUAL =====
def carregar_mesa_individual(nome_arquivo):
    """
    Carrega os dados de uma mesa específica.
    
    Args:
        nome_arquivo (str): Nome do arquivo JSON da mesa
        
    Returns:
        dict: Dados da mesa ou None se erro
    """
    url = f"https://api.github.com/repos/{REPO}/contents/mesas/{nome_arquivo}?ref={BRANCH}"
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        conteudo_base64 = response.json()["content"]
        conteudo = base64.b64decode(conteudo_base64).decode()
        mesa_data = json.loads(conteudo)
        mesa_data["arquivo"] = nome_arquivo  # Adiciona o nome do arquivo para referência
        return mesa_data
    else:
        return None

# ===== FUNÇÃO: CRIAR NOVA MESA =====
def criar_mesa(nome_mesa, descricao, mestre):
    """
    Cria uma nova mesa de RPG.
    
    Args:
        nome_mesa (str): Nome da mesa
        descricao (str): Descrição da mesa
        mestre (str): Nome do mestre da mesa
        
    Returns:
        tuple: (sucesso, mensagem)
    """
    # Gera um ID único para a mesa baseado no timestamp
    import time
    id_mesa = int(time.time())
    
    # Nome do arquivo será baseado no ID da mesa
    nome_arquivo = f"mesa_{id_mesa}.json"
    
    # Estrutura da nova mesa
    nova_mesa = {
        "id": id_mesa,
        "nome": nome_mesa,
        "descricao": descricao,
        "mestre": mestre,
        "jogadores": [],
        "max_jogadores": 6,
        "data_criacao": time.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ativa",
        "configuracoes": {
            "sistema": "Tenebris RPG",
            "nivel_inicial": 1,
            "modo_jogo": "campanha"
        }
    }
    
    # Salva a nova mesa no GitHub
    if salvar_mesa(nome_arquivo, nova_mesa):
        return True, f"Mesa '{nome_mesa}' criada com sucesso! ID: {id_mesa}"
    else:
        return False, "Erro ao criar a mesa."

# ===== FUNÇÃO: SALVAR MESA NO GITHUB =====
def salvar_mesa(nome_arquivo, dados_mesa):
    """
    Salva uma mesa no diretório mesas do GitHub.
    
    Args:
        nome_arquivo (str): Nome do arquivo JSON
        dados_mesa (dict): Dados da mesa
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    url = f"https://api.github.com/repos/{REPO}/contents/mesas/{nome_arquivo}"
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Converte os dados para JSON
    conteudo_json = json.dumps(dados_mesa, indent=2, ensure_ascii=False)
    conteudo_base64 = base64.b64encode(conteudo_json.encode('utf-8')).decode('utf-8')
    
    # Dados para criar o arquivo
    dados = {
        "message": f"Nova mesa criada: {dados_mesa['nome']}",
        "content": conteudo_base64,
        "branch": BRANCH
    }
    
    response = requests.put(url, headers=headers, json=dados)
    return response.status_code == 201  # 201 = Created

# ===== FUNÇÃO: ENTRAR NA MESA =====
def entrar_mesa(mesa_data):
    """
    Permite ao usuário entrar em uma mesa específica.
    
    Args:
        mesa_data (dict): Dados da mesa
    """
    # Armazena a mesa atual no estado da sessão
    st.session_state["mesa_atual"] = mesa_data
    st.session_state["na_mesa"] = True
    st.rerun()

# ===== FUNÇÃO: INTERFACE DA MESA =====
def interface_mesa():
    """
    Renderiza a interface de uma mesa específica.
    """
    if "mesa_atual" not in st.session_state:
        st.error("Erro: Mesa não encontrada.")
        return
    
    mesa = st.session_state["mesa_atual"]
    
    # Cabeçalho da mesa
    st.title(f"🎲 {mesa['nome']}")
    st.markdown(f"**Mestre:** {mesa['mestre']}")
    st.markdown(f"**Descrição:** {mesa['descricao']}")
    
    # Informações da mesa
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Jogadores", f"{len(mesa['jogadores'])}/{mesa['max_jogadores']}")
    
    with col2:
        st.metric("Status", mesa['status'].title())
    
    with col3:
        st.metric("Sistema", mesa['configuracoes']['sistema'])
    
    # Lista de jogadores
    st.subheader("👥 Jogadores")
    if mesa['jogadores']:
        for jogador in mesa['jogadores']:
            st.markdown(f"• {jogador}")
    else:
        st.info("Nenhum jogador na mesa ainda.")
    
    # Botões de ação
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚪 Voltar às Mesas"):
            st.session_state["na_mesa"] = False
            st.session_state["mesa_atual"] = None
            st.rerun()
    
    with col2:
        # Aqui você pode adicionar mais funcionalidades da mesa
        st.button("⚙️ Configurações da Mesa", disabled=True)
    
    # Área de chat/interação (placeholder)
    st.subheader("💬 Chat da Mesa")
    st.info("Sistema de chat em desenvolvimento...")

# ===== FUNÇÃO: PÁGINA DE MESAS =====
def mesas():
    """
    Renderiza a página de mesas com lista de mesas e opção de criar nova mesa.
    """
    st.title("🎲 Mesas de RPG")
    
    # Verifica se está dentro de uma mesa
    if st.session_state.get("na_mesa", False):
        interface_mesa()
        return
    
    # Botão para criar nova mesa
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("➕ Criar Mesa", type="primary"):
            st.session_state["criando_mesa"] = True
    
    # Modal para criar mesa
    if st.session_state.get("criando_mesa", False):
        st.subheader("📝 Criar Nova Mesa")
        
        with st.form("form_criar_mesa"):
            nome_mesa = st.text_input("Nome da Mesa", placeholder="Ex: Aventura na Floresta Sombria")
            descricao = st.text_area("Descrição", placeholder="Descreva a aventura, cenário, etc.")
            
            # Colunas para os botões
            col1, col2 = st.columns(2)
            
            with col1:
                criar = st.form_submit_button("🎲 Criar Mesa", type="primary")
            
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar")
            
            if criar:
                if nome_mesa and descricao:
                    mestre = st.session_state["usuario"]
                    sucesso, mensagem = criar_mesa(nome_mesa, descricao, mestre)
                    
                    if sucesso:
                        st.success(mensagem)
                        st.session_state["criando_mesa"] = False
                        st.rerun()
                    else:
                        st.error(mensagem)
                else:
                    st.error("Por favor, preencha todos os campos.")
            
            if cancelar:
                st.session_state["criando_mesa"] = False
                st.rerun()
    
    # Lista de mesas
    st.subheader("📋 Mesas Disponíveis")
    
    # Carrega as mesas
    mesas_list = carregar_mesas()
    
    if not mesas_list:
        st.info("Nenhuma mesa encontrada. Seja o primeiro a criar uma mesa!")
    else:
        # Exibe cada mesa
        for mesa in mesas_list:
            with st.container():
                st.markdown("---")
                
                # Layout da mesa
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### 🎲 {mesa['nome']}")
                    st.markdown(f"**Mestre:** {mesa['mestre']}")
                    st.markdown(f"**Descrição:** {mesa['descricao']}")
                    
                    # Informações extras
                    info_col1, info_col2, info_col3 = st.columns(3)
                    
                    with info_col1:
                        st.caption(f"👥 {len(mesa['jogadores'])}/{mesa['max_jogadores']} jogadores")
                    
                    with info_col2:
                        st.caption(f"📅 {mesa['data_criacao']}")
                    
                    with info_col3:
                        status_color = "🟢" if mesa['status'] == "ativa" else "🔴"
                        st.caption(f"{status_color} {mesa['status'].title()}")
                
                with col2:
                    # Botão para entrar na mesa
                    if st.button("🚪 Entrar", key=f"entrar_{mesa['id']}"):
                        entrar_mesa(mesa)
                    
                    # Botão de informações (opcional)
                    if st.button("ℹ️ Info", key=f"info_{mesa['id']}"):
                        st.session_state[f"show_info_{mesa['id']}"] = True
                
                # Modal de informações detalhadas (opcional)
                if st.session_state.get(f"show_info_{mesa['id']}", False):
                    with st.expander("ℹ️ Informações Detalhadas", expanded=True):
                        st.json(mesa)
                        if st.button("Fechar", key=f"close_{mesa['id']}"):
                            st.session_state[f"show_info_{mesa['id']}"] = False
                            st.rerun()

# ===== INICIALIZAÇÃO DE ESTADOS PARA MESAS =====
# Adicione essas linhas no final do seu arquivo, junto com as outras inicializações de estado

# Estado para controlar se está criando uma mesa
if "criando_mesa" not in st.session_state:
    st.session_state["criando_mesa"] = False

# Estado para controlar se está dentro de uma mesa
if "na_mesa" not in st.session_state:
    st.session_state["na_mesa"] = False

# Estado para armazenar a mesa atual
if "mesa_atual" not in st.session_state:
    st.session_state["mesa_atual"] = None


# ===== FUNÇÃO: PÁGINA PRINCIPAL =====
def home():
    st.title("EM DESENVOLVIMENTO")




# ===== FUNÇÃO: SIDEBAR =====
def pagina_principal():
    """
    Renderiza a página principal após o login.
    
    Mostra uma mensagem de boas-vindas personalizada e
    oferece a opção de logout.
    """
    
    # Menu lateral estilo lista
    pagina = st.sidebar.radio("Navegação", ["🌒 Home", "🎲 Mesas", "⚙️ Configurações"])

    # Conteúdo da página
    st.title(pagina)

    if "Início" in pagina:
        home()

    elif "Mesas" in pagina:
        mesas()

    elif "Configurações" in pagina:
        st.write("Altere as configurações do sistema.")
    
    
    
    # Botão de logout
    if st.button("Sair"):
        # Limpa o estado da sessão
        st.session_state["logado"] = False
        st.session_state["usuario"] = None
        # Recarrega a página para mostrar a tela de login
        st.rerun()

# ===== CONFIGURAÇÃO INICIAL DA INTERFACE =====

# Configurações iniciais da página web antes de renderizar o conteúdo.

st.set_page_config(
    page_title="Login Tenebris",    # Título da aba do navegador
    page_icon="🌒"                  # Ícone da aba do navegador
)

# ===== INICIALIZAÇÃO DO ESTADO DA SESSÃO =====

# Inicializa as variáveis de estado da sessão se elas não existirem.
# O Streamlit mantém essas variáveis entre as execuções da aplicação.

# Verifica se o usuário está logado
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Armazena o nome do usuário logado
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ===== CONTROLE DE FLUXO PRINCIPAL =====
#
# Controla qual página será exibida baseado no estado de login.
# 
# Se o usuário não está logado, mostra a página de login
if not st.session_state["logado"]:
    pagina_login()
else:
    # Se o usuário está logado, mostra a página principal
    pagina_principal()
