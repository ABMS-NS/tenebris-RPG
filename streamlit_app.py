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

# ===== Interface =====
st.set_page_config(page_title="Login Tenebris", page_icon="🌒")

st.title("🌒 Login - Tenebris RPG")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        usuarios = carregar_usuarios()
        if verificar_login(usuario, senha, usuarios):
            st.session_state["logado"] = True
            st.session_state["usuario"] = usuario
            st.success("Login realizado com sucesso!")
        else:
            st.error("Usuário ou senha inválidos.")
else:
    st.title("✅ DEU CERTO")
    st.write(f"Você está logado como: **{st.session_state['usuario']}**")
    if st.button("Sair"):
        st.session_state["logado"] = False
        st.experimental_rerun()
