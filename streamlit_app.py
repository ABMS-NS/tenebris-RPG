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

Formato JSON: {id: {nome, senha}}

Autor: Sistema Tenebris RPG
Data: 2025
"""

# ===== IMPORTAÇÕES =====
import streamlit as st      # Framework web para criar interfaces interativas
import requests            # Biblioteca para fazer requisições HTTP ao GitHub API
import base64             # Biblioteca para codificar/decodificar arquivos em base64
import json               # Biblioteca para manipular dados JSON

# ===== CONFIGURAÇÕES GLOBAIS =====
#"""
#Configurações essenciais para conexão com o repositório GitHub
#que serve como banco de dados do sistema.
#"""
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
        dict: Dicionário com formato {id: {nome, senha}}
        
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
    Verifica se as credenciais de login são válidas e retorna os dados do usuário.
    
    Percorre o dicionário de usuários e compara o nome de usuário e senha
    fornecidos com os dados armazenados.
    
    Args:
        usuario (str): Nome de usuário fornecido
        senha (str): Senha fornecida
        usuarios (dict): Dicionário de usuários carregado do GitHub {id: {nome, senha}}
        
    Returns:
        tuple: (sucesso, user_id, dados_usuario)
            sucesso (bool): True se as credenciais forem válidas
            user_id (str): ID do usuário ou None se inválido
            dados_usuario (dict): Dados do usuário ou None se inválido
    """
    # Percorre todos os usuários no dicionário
    for user_id, dados in usuarios.items():
        # Verifica se o usuário e senha coincidem
        if dados["nome"] == usuario and dados["senha"] == senha:
            return True, user_id, dados  # Retorna True, ID e dados do usuário
    return False, None, None  # Login inválido

# ===== FUNÇÃO: SALVAR USUÁRIOS NO GITHUB =====
def salvar_usuarios(usuarios):
    """
    Salva o dicionário atualizado de usuários no arquivo JSON do GitHub.
    
    Processo:
    1. Obtém o SHA atual do arquivo (necessário para atualização)
    2. Converte o dicionário de usuários para JSON
    3. Codifica em base64
    4. Faz commit da atualização no GitHub
    
    Args:
        usuarios (dict): Dicionário atualizado de usuários
        
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
    
    # Converte o dicionário de usuários para string JSON formatada
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
        usuarios (dict): Dicionário de usuários existentes
        
    Returns:
        bool: True se o usuário já existe, False caso contrário
    """
    # Percorre todos os usuários no dicionário
    for dados in usuarios.values():
        # Verifica se o nome de usuário já existe
        if dados["nome"] == usuario:
            return True  # Usuário já existe
    return False  # Usuário não existe

# ===== FUNÇÃO: OBTER PRÓXIMO ID =====
def obter_proximo_id(usuarios):
    """
    Calcula o próximo ID disponível para um novo usuário.
    
    Percorre todos os IDs existentes e encontra o maior ID,
    então retorna o próximo número sequencial.
    
    Args:
        usuarios (dict): Dicionário de usuários existentes
        
    Returns:
        str: Próximo ID disponível
    """
    if not usuarios:  # Se não há usuários, começa com ID 1
        return "1"
    
    # Lista para armazenar todos os IDs encontrados
    ids_existentes = []
    
    # Percorre todos os IDs e converte para inteiro
    for user_id in usuarios.keys():
        try:
            ids_existentes.append(int(user_id))
        except ValueError:
            # Se não conseguir converter para int, ignora
            continue
    
    # Se não há IDs válidos, começa com 1
    if not ids_existentes:
        return "1"
    
    # Retorna o maior ID + 1 como string
    return str(max(ids_existentes) + 1)

# ===== FUNÇÃO: CADASTRAR NOVO USUÁRIO =====
def cadastrar_usuario(usuario, senha, usuarios):
    """
    Cadastra um novo usuário no sistema.
    
    Processo:
    1. Verifica se o usuário já existe
    2. Gera um novo ID automático
    3. Cria o objeto do novo usuário
    4. Adiciona ao dicionário de usuários
    5. Salva no GitHub
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha do usuário
        usuarios (dict): Dicionário atual de usuários
        
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
    
    # Cria o objeto do novo usuário
    novo_usuario = {
        "nome": usuario,
        "senha": senha
    }
    
    # Debug: Mostra o novo usuário que será adicionado
    print(f"Debug: Novo usuário criado: ID {novo_id} -> {novo_usuario}")
    
    # Adiciona o novo usuário ao dicionário
    usuarios[novo_id] = novo_usuario
    
    # Debug: Mostra o dicionário completo antes de salvar
    print(f"Debug: Dicionário de usuários antes de salvar: {usuarios}")
    
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
                # Carrega o dicionário de usuários do GitHub
                usuarios = carregar_usuarios()
                
                # Verifica as credenciais e obtém os dados do usuário
                login_valido, user_id, dados_usuario = verificar_login(usuario_login, senha_login, usuarios)
                
                if login_valido:
                    # Login bem-sucedido - atualiza o estado da sessão
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = dados_usuario["nome"]
                    st.session_state["id"] = user_id
                    st.session_state["dados_usuario"] = dados_usuario
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
                        # Carrega dicionário atual de usuários
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

# ===== FUNÇÃO: PÁGINA PRINCIPAL =====
def pagina_principal():
    """
    Renderiza a página principal após o login.
    
    Mostra uma mensagem de boas-vindas personalizada e
    oferece a opção de logout.
    """
    # Título da página principal
    st.title("Página Principal")
    
    # Mensagem de boas-vindas personalizada usando o ID do usuário
    usuario_nome = st.session_state.get("usuario", "Usuário")
    usuario_id = st.session_state.get("id", "N/A")
    
    st.write(f"Bem-vindo, {usuario_nome} (ID: {usuario_id})! Saiba que você é o ser mais desprezível do mundo, eu odeio você seu pedaço de merda ambulante (me estessei fazendo codio de novo)")

    # Botão de logout
    if st.button("Sair"):
        # Limpa o estado da sessão
        st.session_state["logado"] = False
        st.session_state["usuario"] = None
        st.session_state["id"] = None
        st.session_state["dados_usuario"] = None
        # Recarrega a página para mostrar a tela de login
        st.rerun()

# ===== CONFIGURAÇÃO INICIAL DA INTERFACE =====
#"""
#Configurações iniciais da página web antes de renderizar o conteúdo.
#"""
st.set_page_config(
    page_title="Login Tenebris",    # Título da aba do navegador
    page_icon="🌒"                  # Ícone da aba do navegador
)

# ===== INICIALIZAÇÃO DO ESTADO DA SESSÃO =====
#"""
#Inicializa as variáveis de estado da sessão se elas não existirem.
#O Streamlit mantém essas variáveis entre as execuções da aplicação.
#"""
# Verifica se o usuário está logado
if "logado" not in st.session_state:
    st.session_state["logado"] = False

# Armazena o nome do usuário logado
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# Armazena o ID do usuário logado
if "id" not in st.session_state:
    st.session_state["id"] = None

# Armazena todos os dados do usuário logado
if "dados_usuario" not in st.session_state:
    st.session_state["dados_usuario"] = None

# ===== CONTROLE DE FLUXO PRINCIPAL =====
# """
#Controla qual página será exibida baseado no estado de login.
#"""
# Se o usuário não está logado, mostra a página de login
if not st.session_state["logado"]:
    pagina_login()
else:
    # Se o usuário está logado, mostra a página principal
    pagina_principal()