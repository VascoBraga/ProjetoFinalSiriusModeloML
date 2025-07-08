"""
Estilos CSS customizados para a aplicação Streamlit
"""

import streamlit as st

def load_custom_css():
    """Carrega estilos CSS customizados"""
    
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1e3d59;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
        }

        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 0.25rem solid #1e3d59;
            margin: 0.5rem 0;
        }

        .viable-positive {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 0.25rem solid #28a745;
        }

        .viable-negative {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 0.25rem solid #dc3545;
        }

        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
    </style>
    """, unsafe_allow_html=True)