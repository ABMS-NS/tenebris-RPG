import streamlit as st
import requests
import base64
import json
import hashlib

# ===== INSTRUÇÕES DE CONFIGURAÇÃO =====
#"""
# 🔧 COMO CONFIGURAR ESTE SISTEMA:

#1. **Configurar o GitHub:**
#   - Crie um repositório no GitHub
#   - Altere a variável REPO para: "seu_usuario/seu_repositorio"
#   - Crie um Personal Access Token no GitHub com permissões de repo

#2. **Configurar o Streamlit:**
#   - Crie um arquivo .streamlit/secrets.toml na raiz do projeto
#   - Adicione: GITHUB_TOKEN = "seu_token_aqui"
#   - Ou configure nas configurações do Streamlit Cloud

#3. **Executar:**
#   - Execute: streamlit run arquivo.py
#   - O sistema criará automaticamente o arquivo usuarios.json no GitHub

#4. **Funcionalidades:**
#   - ✅ Login com GitHub como banco de dados
#   - ✅ Cadastro de novos usuários
#   - ✅ Senhas criptografadas (SHA-256)
#   - ✅ IDs automáticos
#   - ✅ Timestamps de cadastro
#   - ✅ Validações de campos
#   - ✅ Controle de sessão
#   - ✅ Interface amigável

#5. **Segurança:**
#   - Senhas são criptografadas antes de salvar
#   - Token do GitHub fica nos secrets
#   - Validações de entrada
#   - Controle de acesso por sessão

#Para usar em produção, substitua area_logada() pelo conteúdo do seu site!
#"""

# ===== CONFIGURAÇÕES DO GITHUB =====

# Configurações para usar o GitHub como banco de dados
REPO = "ABMS-NS/tenebris-RPG"  # ALTERE AQUI: seu_usuario/seu_repositorio
ARQUIVO_JSON = "usuarios.json"        # Nome do arquivo que armazena os usuários
BRANCH = "main"                       # Branch do repositório
TOKEN = st.secrets["GITHUB_TOKEN"]    # Token do GitHub nos secrets do Streamlit

# ===== CONFIGURAÇÕES DA PÁGINA =====

st.set_page_config(
    page_title="Sistema de Login",
    page_icon="🔐",
    layout="centered"
)

# ===== FUNÇÕES DE UTILIDADE =====

def criptografar_senha(senha):
    """
    Criptografa a senha usando SHA-256 para segurança básica.
    
    Args:
        senha (str): Senha em texto plano
        
    Returns:
        str: Senha criptografada em hexadecimal
    """
    return hashlib.sha256(senha.encode()).hexdigest()

# ===== FUNÇÕES PARA GITHUB =====

def carregar_usuarios():
    """
    Carrega a lista de usuários do arquivo JSON hospedado no GitHub.
    
    Processo:
    1. Faz requisição GET para a API do GitHub
    2. Decodifica o conteúdo base64 retornado
    3. Converte de JSON para lista Python
    
    Returns:
        list: Lista de usuários cadastrados
    """
    # URL da API do GitHub para acessar o arquivo
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO_JSON}?ref={BRANCH}"
    
    # Headers de autenticação
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Faz a requisição
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # Decodifica o conteúdo base64
            conteudo_base64 = response.json()["content"]
            conteudo = base64.b64decode(conteudo_base64).decode('utf-8')
            return json.loads(conteudo)
        elif response.status_code == 404:
            # Arquivo não existe ainda, retorna lista vazia
            return []
        else:
            st.error(f"❌ Erro ao carregar usuários: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"❌ Erro ao conectar com GitHub: {e}")
        return []

def salvar_usuarios(usuarios):
    """
    Salva a lista de usuários no arquivo JSON do GitHub.
    
    Processo:
    1. Obtém o SHA atual do arquivo (se existir)
    2. Converte a lista para JSON
    3. Codifica em base64
    4. Faz commit no GitHub
    
    Args:
        usuarios (list): Lista de usuários para salvar
        
    Returns:
        bool: True se salvou com sucesso, False caso contrário
    """
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO_JSON}"
    
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # Verifica se o arquivo já existe para obter o SHA
        response = requests.get(url, headers=headers)
        sha_atual = None
        
        if response.status_code == 200:
            sha_atual = response.json()["sha"]
        
        # Converte para JSON e codifica em base64
        conteudo_json = json.dumps(usuarios, indent=2, ensure_ascii=False)
        conteudo_base64 = base64.b64encode(conteudo_json.encode('utf-8')).decode('utf-8')
        
        # Prepara os dados para o commit
        dados = {
            "message": "Atualização de usuários - Sistema de Login",
            "content": conteudo_base64,
            "branch": BRANCH
        }
        
        # Adiciona SHA se o arquivo já existir
        if sha_atual:
            dados["sha"] = sha_atual
        
        # Faz o commit
        response = requests.put(url, headers=headers, json=dados)
        
        return response.status_code in [200, 201]  # 200 = updated, 201 = created
        
    except Exception as e:
        st.error(f"❌ Erro ao salvar no GitHub: {e}")
        return False

def verificar_login(usuario, senha):
    """
    Verifica se as credenciais de login são válidas.
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha em texto plano
        
    Returns:
        bool: True se login válido, False caso contrário
    """
    usuarios = carregar_usuarios()
    senha_criptografada = criptografar_senha(senha)
    
    # Procura o usuário na lista
    for u in usuarios:
        if u["usuario"] == usuario and u["senha"] == senha_criptografada:
            return True
    return False

def usuario_existe(usuario):
    """
    Verifica se um usuário já existe no sistema.
    
    Args:
        usuario (str): Nome de usuário para verificar
        
    Returns:
        bool: True se usuário existe, False caso contrário
    """
    usuarios = carregar_usuarios()
    return any(u["usuario"] == usuario for u in usuarios)

def obter_proximo_id(usuarios):
    """
    Calcula o próximo ID disponível para um novo usuário.
    
    Args:
        usuarios (list): Lista de usuários existentes
        
    Returns:
        int: Próximo ID disponível
    """
    if not usuarios:
        return 1
    
    # Busca o maior ID existente
    ids_existentes = [u.get("id", 0) for u in usuarios if isinstance(u.get("id"), int)]
    
    if not ids_existentes:
        return 1
    
    return max(ids_existentes) + 1

def cadastrar_usuario(usuario, senha):
    """
    Cadastra um novo usuário no sistema GitHub.
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha em texto plano
        
    Returns:
        tuple: (sucesso, mensagem)
    """
    # Validações básicas
    if len(usuario) < 3:
        return False, "Usuário deve ter pelo menos 3 caracteres!"
    
    if len(senha) < 4:
        return False, "Senha deve ter pelo menos 4 caracteres!"
    
    # Verifica se usuário já existe
    if usuario_existe(usuario):
        return False, "Usuário já existe!"
    
    # Carrega usuários existentes
    usuarios = carregar_usuarios()
    
    # Cria novo usuário
    novo_id = obter_proximo_id(usuarios)
    import datetime
    
    novo_usuario = {
        "id": novo_id,
        "usuario": usuario,
        "senha": criptografar_senha(senha),
        "data_cadastro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Adiciona à lista
    usuarios.append(novo_usuario)
    
    # Salva no GitHub
    if salvar_usuarios(usuarios):
        return True, f"Usuário cadastrado com sucesso! ID: {novo_id}"
    else:
        return False, "Erro ao salvar usuário no GitHub!"

# ===== INTERFACE DE LOGIN =====

def tela_login():
    """
    Renderiza a tela de login com abas para Login e Cadastro.
    """
    # Título principal
    st.title("🔐 Sistema de Login")
    st.markdown("*Feito por Alison*")
    st.markdown("---")
    
    # Cria abas para Login e Cadastro
    tab_login, tab_cadastro = st.tabs(["🔑 Fazer Login", "👤 Criar Conta"])
    
    # === ABA DE LOGIN ===
    with tab_login:
        st.subheader("Entre com suas credenciais")
        
        # Formulário de login
        with st.form("form_login"):
            usuario = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            
            # Botão de login
            btn_login = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
            
            # Processa o login
            if btn_login:
                if not usuario or not senha:
                    st.error("⚠️ Por favor, preencha todos os campos!")
                else:
                    # Mostra loading enquanto verifica
                    with st.spinner("🔍 Verificando credenciais..."):
                        if verificar_login(usuario, senha):
                            # Login bem-sucedido
                            st.session_state["logado"] = True
                            st.session_state["usuario"] = usuario
                            st.success("✅ Login realizado com sucesso!")
                            st.rerun()
                        else:
                            st.error("❌ Usuário ou senha incorretos!")
    
    # === ABA DE CADASTRO ===
    with tab_cadastro:
        st.subheader("Criar nova conta")
        
        # Formulário de cadastro
        with st.form("form_cadastro"):
            novo_usuario = st.text_input("👤 Usuário", placeholder="Escolha um nome de usuário")
            nova_senha = st.text_input("🔒 Senha", type="password", placeholder="Crie uma senha")
            confirmar_senha = st.text_input("🔒 Confirmar Senha", type="password", placeholder="Confirme sua senha")
            
            # Botão de cadastro
            btn_cadastro = st.form_submit_button("📝 Criar Conta", type="secondary", use_container_width=True)
            
            # Processa o cadastro
            if btn_cadastro:
                if not novo_usuario or not nova_senha or not confirmar_senha:
                    st.error("⚠️ Por favor, preencha todos os campos!")
                elif nova_senha != confirmar_senha:
                    st.error("❌ As senhas não coincidem!")
                else:
                    # Mostra loading enquanto cadastra
                    with st.spinner("📝 Criando conta no GitHub..."):
                        sucesso, mensagem = cadastrar_usuario(novo_usuario, nova_senha)
                        
                        if sucesso:
                            st.success(f"✅ {mensagem}")
                            st.info("🎉 Agora você pode fazer login!")
                        else:
                            st.error(f"❌ {mensagem}")

def area_logada():
    """
    Área que aparece após o login bem-sucedido.
    Aqui você pode colocar o conteúdo do seu site.
    """
    # Cabeçalho com boas-vindas
    st.title(f"🎉 Bem-vindo, {st.session_state['usuario']}!")
    st.markdown("---")
    
    # Informações do usuário
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.success("✅ Você está logado no sistema!")
        st.info("🚀 Dados sincronizados com GitHub")
    
    with col2:
        # Botão de logout
        if st.button("🚪 Sair", type="secondary", use_container_width=True):
            # Limpa o estado da sessão
            st.session_state["logado"] = False
            st.session_state["usuario"] = None
            st.success("👋 Logout realizado com sucesso!")
            st.rerun()
    
    # Exemplo de conteúdo após login
    st.markdown("---")
    st.subheader("📋 Área Restrita")
    
    # Aqui você pode adicionar o conteúdo específico do seu site
    st.write("🎯 **Substitua esta seção pelo conteúdo do seu site!**")
    
    # Exemplo: Mostrar informações dos usuários (só para demonstração)
    if st.checkbox("🔍 Mostrar informações de debug"):
        with st.expander("📊 Informações da Sessão"):
            st.json({
                "Usuario": st.session_state["usuario"],
                "Status": "Logado",
                "Repositorio": REPO,
                "Arquivo": ARQUIVO_JSON
            })
        
        # Botão para visualizar usuários cadastrados (só para debug)
        if st.button("👥 Ver usuários cadastrados"):
            with st.spinner("📥 Carregando do GitHub..."):
                usuarios = carregar_usuarios()
                st.write(f"**Total de usuários:** {len(usuarios)}")
                
                # Mostra usuários sem mostrar senhas
                for u in usuarios:
                    st.write(f"• **ID:** {u.get('id', 'N/A')} | **Usuário:** {u.get('usuario', 'N/A')} | **Cadastro:** {u.get('data_cadastro', 'N/A')}")

# ===== INICIALIZAÇÃO DO ESTADO DA SESSÃO =====

# Inicializa variáveis de estado se não existirem
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# ===== CONTROLE PRINCIPAL DA APLICAÇÃO =====

# Controla qual tela mostrar baseado no estado de login
if not st.session_state["logado"]:
    # Usuário não está logado - mostra tela de login
    tela_login()
else:
    # Usuário está logado - mostra área restrita
    # Redireciona para a página "Home" (nome do arquivo: 1_Home.py)
    st.markdown('<meta http-equiv="refresh" content="0;url=/1_Home">', unsafe_allow_html=True)
