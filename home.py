import streamlit as st
from datetime import datetime
from mesas import display_mesas

def home(usuario):
    # Header com estilo melhorado
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #00FFD1; font-size: 3rem; margin-bottom: 0.5rem; font-family: monospace;">🏠 HOME</h1>
        <p style="color: #FFFFFF; font-size: 1.2rem; font-family: monospace;">Bem-vindo ao seu painel principal</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Adicionar espaçamento
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Layout das colunas com melhor espaçamento
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        # Card para Mesas
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #00FFD1; margin-bottom: 1rem;">
            <h3 style="color: #00FFD1; margin-bottom: 1rem; font-family: monospace;">🎲 Mesas Disponíveis</h3>
            <p style="color: #FFFFFF; margin-bottom: 1rem; font-family: monospace;">Encontre e participe de mesas de RPG ativas</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 Acessar Mesas", key="btn_mesas", use_container_width=True):
            st.success("Redirecionando para mesas...")
            display_mesas()

    with col2:
        # Card para Rolagens
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #00FFD1; margin-bottom: 1rem;">
            <h3 style="color: #00FFD1; margin-bottom: 1rem; font-family: monospace;">🎲 Rolagens Simples</h3>
            <p style="color: #FFFFFF; margin-bottom: 1rem; font-family: monospace;">Faça rolagens de dados rapidamente</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎲 Fazer Rolagem", key="btn_rolagem", use_container_width=True):
            st.success("Redirecionando para rolagens simples...")
    
    with col3:
        # Card para Perfil
        st.markdown("""
        <div style="background-color: #1E1E1E; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #00FFD1; margin-bottom: 1rem;">
            <h3 style="color: #00FFD1; margin-bottom: 1rem; font-family: monospace;">👤 Perfil do Usuário</h3>
            <p style="color: #FFFFFF; margin-bottom: 1rem; font-family: monospace;">Gerencie suas informações pessoais</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Exibir informações do usuário com estilo
        st.markdown(f"""
        <div style="background-color: #121212; padding: 1rem; border-radius: 8px; text-align: center; border: 1px solid #00FFD1;">
            <h4 style="color: #00FFD1; margin: 0; font-family: monospace;">Olá, {usuario}!</h4>
            <p style="color: #FFFFFF; margin: 0.5rem 0 0 0; font-size: 0.9rem; font-family: monospace;">
                {datetime.now().strftime('%d/%m/%Y - %H:%M')}
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Adicionar espaçamento no final
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Footer com informações adicionais
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #FFFFFF; font-size: 0.9rem; padding: 1rem 0; font-family: monospace;">
        <p>🎮 Plataforma de RPG Online | Versão 1.0</p>
    </div>
    """, unsafe_allow_html=True)