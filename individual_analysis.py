"""
Página de análise individual de causas
"""

import streamlit as st
import plotly.graph_objects as go

def show_individual_analysis(analyzer):
    """Página principal - análise individual"""
    
    st.header("🔍 Análise Individual de Causa")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 Dados da Causa")

        # Formulário de entrada
        with st.form("causa_form"):

            # Dados básicos
            st.markdown("#### 📋 Informações Básicas")

            tipo_assunto = st.selectbox(
                "Tipo de Assunto:",
                ["Telefonia/Internet", "Bancos/Financeiro", "Energia Elétrica",
                 "Comércio/Produto", "Plano de Saúde", "Transporte Aéreo", "Outros"]
            )

            problema_principal = st.selectbox(
                "Problema Principal:",
                ["Cobrança Indevida", "Produto Defeituoso", "Serviço Não Prestado",
                 "Dano Moral", "Negativação Indevida", "Cancelamento Unilateral", "Outros"]
            )

            valor_causa = st.number_input(
                "Valor Estimado da Causa (R$):",
                min_value=100.0,
                max_value=100000.0,
                value=3000.0,
                step=100.0,
                help="Valor estimado em reais"
            )

            confianca = st.slider(
                "Confiança na Estimativa:",
                min_value=0.1,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Quão confiante você está na estimativa de valor"
            )

            # Dados geográficos
            st.markdown("#### 🗺️ Localização")

            col_geo1, col_geo2 = st.columns(2)
            with col_geo1:
                regiao = st.selectbox(
                    "Região:",
                    ["Sudeste", "Sul", "Centro-oeste", "Nordeste", "Norte"]
                )

            with col_geo2:
                uf_options = {
                    "Sudeste": ["SP", "RJ", "MG", "ES"],
                    "Sul": ["RS", "SC", "PR"],
                    "Centro-oeste": ["GO", "MT", "MS", "DF"],
                    "Nordeste": ["BA", "PE", "CE", "MA", "PB", "RN", "AL", "SE", "PI"],
                    "Norte": ["PA", "AM", "RO", "AC", "RR", "AP", "TO"]
                }

                uf = st.selectbox("UF:", uf_options[regiao])

            # Dados do consumidor
            st.markdown("#### 👤 Perfil do Consumidor")

            col_dem1, col_dem2 = st.columns(2)
            with col_dem1:
                sexo = st.selectbox("Sexo:", ["M", "F"])

            with col_dem2:
                faixa_etaria_map = {
                    "Até 20 anos": 1,
                    "21 a 30 anos": 2,
                    "31 a 40 anos": 3,
                    "41 a 50 anos": 4,
                    "51 a 60 anos": 5,
                    "61 a 70 anos": 6,
                    "Mais de 70 anos": 7
                }

                faixa_etaria_str = st.selectbox(
                    "Faixa Etária:",
                    list(faixa_etaria_map.keys())
                )
                faixa_etaria = faixa_etaria_map[faixa_etaria_str]

            # Dados temporais
            ano = st.selectbox(
                "Ano da Causa:",
                [2024, 2023, 2022, 2021, 2020]
            )

            # Botão de análise
            submit_button = st.form_submit_button("🚀 Analisar Viabilidade", use_container_width=True)

    with col2:
        st.subheader("📊 Resultado da Análise")

        if submit_button:
            # Prepara dados
            input_data = {
                'tipo_assunto': tipo_assunto,
                'problema_principal': problema_principal,
                'valor_causa': valor_causa,
                'confianca': confianca,
                'regiao': regiao,
                'uf': uf,
                'sexo': sexo,
                'faixa_etaria': faixa_etaria,
                'ano': ano
            }

            # Faz predição
            with st.spinner("🔄 Analisando causa..."):
                result = analyzer.predict_viability(input_data)

            if result:
                # Resultado principal
                if result['prediction'] == 1:
                    st.markdown("""
                    <div class="viable-positive">
                        <h3>✅ CAUSA VIÁVEL</h3>
                        <p>Recomendação: <strong>ACEITAR</strong> esta causa</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="viable-negative">
                        <h3>❌ CAUSA NÃO VIÁVEL</h3>
                        <p>Recomendação: <strong>REJEITAR</strong> esta causa</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Métricas detalhadas
                st.markdown("#### 📈 Probabilidades")

                col_prob1, col_prob2 = st.columns(2)
                with col_prob1:
                    st.metric(
                        "Probabilidade VIÁVEL",
                        f"{result['probability_viavel']:.1%}",
                        delta=f"Confiança: {result['confidence']:.1%}"
                    )

                with col_prob2:
                    st.metric(
                        "Probabilidade NÃO VIÁVEL",
                        f"{result['probability_nao_viavel']:.1%}"
                    )

                # Gráfico de probabilidades
                fig = go.Figure(data=[
                    go.Bar(
                        x=['Não Viável', 'Viável'],
                        y=[result['probability_nao_viavel'], result['probability_viavel']],
                        marker_color=['#ff6b6b', '#4ecdc4']
                    )
                ])

                fig.update_layout(
                    title="Distribuição de Probabilidades",
                    yaxis_title="Probabilidade",
                    yaxis=dict(range=[0, 1])
                )

                st.plotly_chart(fig, use_container_width=True)

                # Fatores influenciadores
                show_interpretation(input_data, result)

            else:
                st.error("❌ Erro na análise. Verifique os dados e tente novamente.")

def show_interpretation(input_data, result):
    """Mostra interpretação dos resultados"""
    
    st.markdown("#### 🎯 Fatores Influenciadores")

    factors = []

    # Análise do valor
    valor = input_data['valor_causa']
    if valor >= 5000:
        factors.append(("✅ Valor Alto", f"R$ {valor:,.2f} - Valor elevado aumenta viabilidade"))
    elif valor >= 2000:
        factors.append(("⚠️ Valor Médio", f"R$ {valor:,.2f} - Valor moderado"))
    else:
        factors.append(("❌ Valor Baixo", f"R$ {valor:,.2f} - Valor baixo reduz viabilidade"))

    # Análise da região
    regiao = input_data['regiao']
    if regiao in ['Sudeste', 'Sul']:
        factors.append(("✅ Região Favorável", f"{regiao} - Histórico de maior sucesso"))
    elif regiao == 'Centro-oeste':
        factors.append(("⚠️ Região Neutra", f"{regiao} - Performance média"))
    else:
        factors.append(("❌ Região Desafiadora", f"{regiao} - Maior dificuldade histórica"))

    # Análise do tipo
    tipo = input_data['tipo_assunto']
    if tipo in ['Bancos/Financeiro', 'Telefonia/Internet']:
        factors.append(("✅ Setor Consolidado", f"{tipo} - Jurisprudência favorável"))
    else:
        factors.append(("⚠️ Setor Variável", f"{tipo} - Sucesso depende do caso"))

    # Análise do problema
    problema = input_data['problema_principal']
    if problema in ['Cobrança Indevida', 'Dano Moral', 'Negativação Indevida']:
        factors.append(("✅ Problema Comum", f"{problema} - Alta taxa de sucesso"))
    else:
        factors.append(("⚠️ Problema Específico", f"{problema} - Análise caso a caso"))

    for factor, description in factors:
        st.markdown(f"**{factor}**: {description}")