"""
Página com informações sobre o sistema
"""

import streamlit as st

def show_about():
    """Informações sobre o sistema"""
    
    st.header("ℹ️ Sobre o Sistema")

    st.markdown("""
    ## 🎯 Objetivo

    Este sistema utiliza **Machine Learning** para analisar a viabilidade de causas jurídicas,
    ajudando escritórios de advocacia a tomar decisões mais informadas sobre quais casos aceitar.

    ## 🧠 Como Funciona

    1. **Coleta de Dados**: O sistema analisa informações sobre:
       - Tipo de assunto e problema
       - Valor estimado da causa
       - Localização geográfica
       - Perfil do consumidor

    2. **Análise com IA**: Utiliza algoritmos de Machine Learning treinados em dados históricos

    3. **Resultado**: Fornece:
       - Classificação (Viável/Não Viável)
       - Probabilidades detalhadas
       - Fatores influenciadores

    ## 📊 Precisão do Modelo

    - **AUC**: ~0.75-0.85 (Excelente)
    - **Precision**: ~0.70-0.80
    - **Recall**: ~0.70-0.80

    ## ⚖️ Considerações Legais

    ⚠️ **Importante**: Este sistema é uma **ferramenta de apoio** à decisão.

    - Não substitui a análise jurídica especializada
    - Deve ser usado em conjunto com conhecimento jurídico
    - A decisão final sempre cabe ao advogado responsável

    ## 🔧 Suporte Técnico

    Para dúvidas ou problemas técnicos, entre em contato com o desenvolvedor.

    ---

    **Versão**: 1.0
    **Última Atualização**: Julho 2025
    """)