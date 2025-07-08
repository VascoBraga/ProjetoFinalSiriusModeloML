#!/usr/bin/env python3
"""
Sistema de Análise de Viabilidade Jurídica
Arquivo principal da aplicação Streamlit
"""

import streamlit as st
from utils.styles import load_custom_css
from pages.individual_analysis import show_individual_analysis
from pages.batch_analysis import show_batch_analysis
from pages.dashboard import show_dashboard
from pages.about import show_about
from utils.model_handler import show_model_upload_section
from juridical_analyzer import load_analyzer

# Configuração da página
st.set_page_config(
    page_title="⚖️ Analisador de Viabilidade Jurídica",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Função principal da aplicação"""
    
    # Carrega CSS customizado
    load_custom_css()
    
    # Header principal
    st.markdown('<h1 class="main-header">⚖️ Analisador de Viabilidade Jurídica</h1>',
                unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem; color: #666;">
        Sistema inteligente para análise de viabilidade de causas jurídicas baseado em Machine Learning
    </div>
    """, unsafe_allow_html=True)

    # Verifica se modelo está carregado
    analyzer = load_analyzer()
    if not st.session_state.get('model_loaded', False):
        show_model_upload_section()
        return

    # Sidebar para navegação
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/1e3d59/ffffff?text=LOGO",
                caption="Sistema de Análise Jurídica")

        page = st.selectbox(
            "📋 Escolha uma opção:",
            ["🔍 Análise Individual", "📊 Análise em Lote", "📈 Dashboard", "ℹ️ Sobre o Sistema"]
        )

    # Roteamento de páginas
    if page == "🔍 Análise Individual":
        show_individual_analysis(analyzer)
    elif page == "📊 Análise em Lote":
        show_batch_analysis(analyzer)
    elif page == "📈 Dashboard":
        show_dashboard()
    elif page == "ℹ️ Sobre o Sistema":
        show_about()

if __name__ == "__main__":
    main()