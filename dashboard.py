"""
Dashboard com estatísticas e insights do sistema
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def show_dashboard():
    """Dashboard com estatísticas e insights"""
    
    st.header("📈 Dashboard - Insights do Sistema")

    # Simulação de dados históricos
    if st.button("📊 Gerar Relatório de Performance"):

        # Dados simulados
        np.random.seed(42)
        dados_simulados = {
            'Mês': ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'],
            'Casos_Analisados': [150, 180, 220, 190, 240, 210],
            'Taxa_Viabilidade': [0.72, 0.68, 0.75, 0.70, 0.73, 0.71],
            'Valor_Medio': [3200, 3500, 3100, 3400, 3300, 3250]
        }

        df_dashboard = pd.DataFrame(dados_simulados)

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.line(df_dashboard, x='Mês', y='Casos_Analisados',
                          title='Casos Analisados por Mês')
            st.plotly_chart(fig1, use_container_width=True)

            fig3 = px.bar(df_dashboard, x='Mês', y='Valor_Medio',
                         title='Valor Médio das Causas')
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            fig2 = px.line(df_dashboard, x='Mês', y='Taxa_Viabilidade',
                          title='Taxa de Viabilidade (%)')
            st.plotly_chart(fig2, use_container_width=True)

            # Distribuição por tipo
            tipos = ['Telefonia', 'Bancos', 'Energia', 'Outros']
            valores = [35, 25, 20, 20]

            fig4 = px.pie(values=valores, names=tipos,
                         title='Distribuição por Tipo de Assunto')
            st.plotly_chart(fig4, use_container_width=True)