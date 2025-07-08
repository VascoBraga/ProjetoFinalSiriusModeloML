"""
Página de análise em lote de múltiplas causas
"""

import streamlit as st
import pandas as pd

def show_batch_analysis(analyzer):
    """Análise em lote de múltiplas causas"""
    
    st.header("📊 Análise em Lote")

    st.markdown("""
    Faça upload de um arquivo CSV com múltiplas causas para análise em lote.

    **Formato esperado do CSV:**
    - `tipo_assunto`: Tipo do assunto
    - `valor_causa`: Valor estimado
    - `regiao`: Região
    - `uf`: UF
    - (outras colunas conforme análise individual)
    """)

    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "Faça upload do arquivo CSV",
        type=['csv'],
        help="Arquivo CSV com dados das causas"
    )

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)

            st.subheader("📋 Dados Carregados")
            st.dataframe(df.head(10))

            if st.button("🚀 Analisar Todas as Causas"):
                with st.spinner("🔄 Processando análise em lote..."):

                    # Processa cada linha
                    results = []

                    for idx, row in df.iterrows():
                        input_data = row.to_dict()
                        result = analyzer.predict_viability(input_data)

                        if result:
                            results.append({
                                'Linha': idx + 1,
                                'Viável': 'SIM' if result['prediction'] == 1 else 'NÃO',
                                'Prob_Viável': f"{result['probability_viavel']:.1%}",
                                'Prob_Não_Viável': f"{result['probability_nao_viavel']:.1%}",
                                'Confiança': f"{result['confidence']:.1%}"
                            })

                    # Mostra resultados
                    if results:
                        results_df = pd.DataFrame(results)

                        st.subheader("📊 Resultados da Análise")
                        st.dataframe(results_df)

                        # Estatísticas
                        viáveis = len([r for r in results if r['Viável'] == 'SIM'])
                        total = len(results)

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Total Analisado", total)
                        with col2:
                            st.metric("Causas Viáveis", viáveis)
                        with col3:
                            st.metric("Taxa de Viabilidade", f"{viáveis/total:.1%}")

                        # Download dos resultados
                        csv = results_df.to_csv(index=False)
                        st.download_button(
                            "💾 Download Resultados",
                            csv,
                            "resultados_analise.csv",
                            "text/csv"
                        )

        except Exception as e:
            st.error(f"❌ Erro ao processar arquivo: {e}")