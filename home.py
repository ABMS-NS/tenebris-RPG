import streamlit as st
from datetime import datetime
from mesas import display_mesas

def home(usuario):
    st.title("HOME")
    st.divider()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Mesas disponíveis")
        if st.button("Ir parar mesas"):
            st.write("Redirecionando para mesas...")
            display_mesas()


    with col2:
        st.subheader("Rolagens simples")
        if st.button("Rolagem simples"):
            st.write("Redirecionando para rolagens simples...")
    
    with col3:
        st.subheader("Perfil do usuário")
        st.subheader(usuario)
