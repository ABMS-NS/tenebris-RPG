import streamlit as st
from datetime import datetime

def home():
    # CSS customizado para estilização
    st.markdown("""
    <style>
    .main-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        color: #8B0000;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        margin-bottom: 0;
    }
    
    .subtitle {
        font-size: 1.1rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .info-card {
        background: linear-gradient(135deg, #1a1a1a, #2d2d2d);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #8B0000;
        margin: 2rem 0;
        color: white;
        text-align: center;
    }
    
    .menu-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #8B0000;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .menu-card:hover {
        transform: translateY(-2px);
    }
    
    .quick-access {
        background: #e9ecef;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        color: #666;
        margin-top: 3rem;
        padding-top: 2rem;
        border-top: 1px solid #ddd;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Título principal
    st.markdown('<h1 class="main-title">⚔️ TENEBRIS RPG ⚔️</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema de Gerenciamento de Campanha - Criado por Alison</p>', unsafe_allow_html=True)
    
    # Descrição do sistema
    st.markdown("""
    <div class="info-card">
        <h2>🌟 Central de Comando do Mestre</h2>
        <p>Bem-vindo ao sistema de gerenciamento da campanha TENEBRIS! Aqui você pode organizar 
        todos os aspectos da sua aventura: personagens dos jogadores, NPCs, localizações, 
        itens, magias e muito mais.</p>
        
        <p>Mantenha sua campanha organizada e acessível em um só lugar!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Menu principal
    st.markdown("## 📋 Menu Principal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="menu-card">
            <h3>👥 Personagens</h3>
            <p>Gerencie fichas dos jogadores, NPCs importantes, inimigos e aliados. 
            Acompanhe níveis, atributos, equipamentos e histórico.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="menu-card">
            <h3>🗺️ Localizações</h3>
            <p>Organize cidades, masmorras, regiões e pontos de interesse. 
            Mantenha descrições, mapas e informações importantes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="menu-card">
            <h3>📖 Sessões</h3>
            <p>Registre o que aconteceu em cada sessão, decisões importantes 
            dos jogadores e progressão da história.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="menu-card">
            <h3>⚔️ Itens & Equipamentos</h3>
            <p>Catálogo completo de armas, armaduras, itens mágicos e tesouros. 
            Controle o que cada personagem possui.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="menu-card">
            <h3>🔮 Magias & Habilidades</h3>
            <p>Banco de dados de magias, habilidades especiais e poderes. 
            Organize por escola, nível e tipo.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="menu-card">
            <h3>📚 Lore & História</h3>
            <p>Mantenha a mitologia, história do mundo, facções, 
            eventos importantes e cronologia da campanha.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Acesso rápido
    st.markdown("## ⚡ Acesso Rápido")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎭 Fichas dos PJs", key="pj_sheets"):
            st.info("Redirecionando para fichas dos personagens...")
    
    with col2:
        if st.button("🎲 Rolagem Rápida", key="quick_roll"):
            st.info("Abrindo sistema de rolagem...")
    
    with col3:
        if st.button("📝 Nova Anotação", key="new_note"):
            st.info("Criando nova anotação...")
    
    with col4:
        if st.button("🔍 Buscar Info", key="search"):
            st.info("Abrindo busca no sistema...")
    
    # Status da campanha
    st.markdown("## 📊 Status da Campanha")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="quick-access">
            <h4>🎯 Sessão Atual</h4>
            <p><strong>Sessão #12</strong><br>
            Local: Ruínas de Valdris<br>
            Próxima: Sábado, 20:00</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="quick-access">
            <h4>👥 Grupo Ativo</h4>
            <p><strong>4 Jogadores</strong><br>
            Nível médio: 8<br>
            Status: Explorando</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="quick-access">
            <h4>📈 Progresso</h4>
            <p><strong>Capítulo 3</strong><br>
            Arco: A Conspiração<br>
            Conclusão: 65%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Lembretes/Notas rápidas
    st.markdown("## 📌 Lembretes do Mestre")
    
    with st.expander("🔥 Pendências para próxima sessão"):
        st.write("""
        - Preparar encontro com o Lorde Sombrio
        - Revisar magias do novo item mágico encontrado
        - Definir consequências das ações dos PJs na cidade
        - Criar NPCs para a taverna "O Javali Dourado"
        """)
    
    with st.expander("💡 Ideias para desenvolvimento"):
        st.write("""
        - Introduzir subplot sobre a guerra civil
        - Desenvolver romance entre NPCs
        - Criar missão secundária na floresta
        - Expandir lore sobre os Antigos
        """)
    
    # Rodapé
    st.markdown("""
    <div class="footer">
        <p>🎲 TENEBRIS RPG - Sistema de Gerenciamento | Desenvolvido por Alison</p>
        <p>Última atualização: {}</p>
    </div>
    """.format(datetime.now().strftime("%d/%m/%Y às %H:%M")), unsafe_allow_html=True)