import streamlit as st

if "logado" not in st.session_state or not st.session_state["logado"]:
    st.warning("⚠️ Acesso não autorizado! Faça login primeiro.")
    st.stop()

st.title(f"🎉 Bem-vindo, {st.session_state['usuario']}!")
