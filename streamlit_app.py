import streamlit as st
import requests
import base64
import json

# ===== CONFIGURAÇÕES =====
REPO = "ABMS-NS/tenebris-RPG"
ARQUIVO_JSON = "usuarios.json"
BRANCH = "main"
TOKEN = st.secrets["GITHUB_TOKEN"]

# ===== Função: Carregar lista de usuários =====
def carregar_usuarios():
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO_JSON}?ref={BRANCH}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
        }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        conteudo_base64 = response.json()["content"]
        conteudo = base64.b64decode(conteudo_base64).decode()
        return json.loads(conteudo)
    else:
        st.error("❌ Não foi possível carregar o banco de dados.")
        st.stop()

# ===== Função: Verificar login =====
def verificar_login(usuario, senha, usuarios):
    for u in usuarios:
        if u["usuario"] == usuario and u["senha"] == senha:
            return True
    return False

# ===== Função: Salvar usuários no GitHub =====
def salvar_usuarios(usuarios):
    url = f"https://api.github.com/repos/{REPO}/contents/{ARQUIVO_JSON}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Primeiro, pegar o SHA atual do arquivo
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha_atual = response.json()["sha"]
    else:
        st.error("❌ Erro ao acessar o arquivo no GitHub.")
        return False
    
    # Preparar o conteúdo para upload
    conteudo_json = json.dumps(usuarios, indent=2, ensure_ascii=False)
    conteudo_base64 = base64.b64encode(conteudo_json.encode()).decode()
    
    # Fazer o commit
    dados = {
        "message": "Novo usuário cadastrado",
        "content": conteudo_base64,
        "sha": sha_atual,
        "branch": BRANCH
    }
    
    response = requests.put(url, headers=headers, json=dados)
    return response.status_code == 200

# ===== Função: Verificar se usuário já existe =====
def usuario_existe(usuario, usuarios):
    for u in usuarios:
        if u["usuario"] == usuario:
            return True
    return False

# ===== Função: Cadastrar novo usuário =====
def cadastrar_usuario(usuario, senha, usuarios):
    if usuario_existe(usuario, usuarios):
        return False, "Usuário já existe."
    
    novo_usuario = {"usuario": usuario, "senha": senha}
    usuarios.append(novo_usuario)
    
    if salvar_usuarios(usuarios):
        return True, "Usuário cadastrado com sucesso!"
    else:
        return False, "Erro ao salvar usuário."

# ===== Função: Página de Login =====
def pagina_login():
    st.title("🌒 Login - Tenebris RPG")
    
    # Tabs para alternar entre Login e Cadastro
    tab1, tab2 = st.tabs(["🔑 Login", "👤 Cadastro"])
    
    with tab1:
        st.subheader("Fazer Login")
        usuario_login = st.text_input("Usuário", key="login_usuario")
        senha_login = st.text_input("Senha", type="password", key="login_senha")

        if st.button("Entrar", key="btn_login"):
            if usuario_login and senha_login:
                usuarios = carregar_usuarios()
                if verificar_login(usuario_login, senha_login, usuarios):
                    st.session_state["logado"] = True
                    st.session_state["usuario"] = usuario_login
                    st.rerun()
                else:
                    st.error("Usuário ou senha inválidos.")
            else:
                st.warning("Por favor, preencha todos os campos.")
    
    with tab2:
        st.subheader("Cadastrar Novo Usuário")
        usuario_cadastro = st.text_input("Novo Usuário", key="cadastro_usuario")
        senha_cadastro = st.text_input("Nova Senha", type="password", key="cadastro_senha")
        confirmar_senha = st.text_input("Confirmar Senha", type="password", key="confirmar_senha")

        if st.button("Cadastrar", key="btn_cadastro"):
            if usuario_cadastro and senha_cadastro and confirmar_senha:
                if senha_cadastro == confirmar_senha:
                    if len(usuario_cadastro) >= 3 and len(senha_cadastro) >= 4:
                        usuarios = carregar_usuarios()
                        sucesso, mensagem = cadastrar_usuario(usuario_cadastro, senha_cadastro, usuarios)
                        if sucesso:
                            st.success(mensagem)
                            st.info("Agora você pode fazer login com suas credenciais.")
                        else:
                            st.error(mensagem)
                    else:
                        st.error("Usuário deve ter pelo menos 3 caracteres e senha pelo menos 4 caracteres.")
                else:
                    st.error("As senhas não coincidem.")
            else:
                st.warning("Por favor, preencha todos os campos.")

# ===== Função: Página Principal =====
def pagina_principal():
    st.title("Página Principal")
    st.write(f"Bem-vindo, {st.session_state['usuario']}! Saiba que você é o ser mais desprezível do mundo, eu odeio você seu pedaço de merda ambulante (me estessei fazendo codio de novo)")


    if st.button("Sair"):
        st.session_state["logado"] = False
        st.session_state["usuario"] = None
        st.rerun()

# ===== Interface Principal =====
st.set_page_config(page_title="Login Tenebris", page_icon="🌒")

# Inicializar estado da sessão
if "logado" not in st.session_state:
    st.session_state["logado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# Controle de páginas
if not st.session_state["logado"]:
    pagina_login()
else:
    pagina_principal()