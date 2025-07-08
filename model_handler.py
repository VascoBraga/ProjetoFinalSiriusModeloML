"""
Utilitários para manipulação de modelos
"""

import streamlit as st

def show_model_upload_section():
    """Seção para upload do modelo quando não está disponível"""
    
    st.warning("⚠️ Modelo não encontrado no sistema!")

    st.markdown("""
    ### 📤 Upload do Modelo

    Para usar o sistema, você precisa fazer upload do modelo treinado:

    1. **Treine o modelo** executando o pipeline de ML
    2. **Salve o modelo** com o código abaixo:
    3. **Faça upload** do arquivo gerado
    """)

    st.code("""
# Código para salvar o modelo após treinamento:
import pickle

# Supondo que você tenha o modelo treinado em 'modelo'
model_data = {
    'model': modelo,  # Seu modelo treinado
    'feature_names': feature_names,  # Lista de nomes das features
    'scaler': scaler  # Scaler se usado (opcional)
}

with open('modelo_viabilidade_final.pkl', 'wb') as f:
    pickle.dump(model_data, f)

print("✅ Modelo salvo como: modelo_viabilidade_final.pkl")
""")

    # Upload do arquivo
    uploaded_file = st.file_uploader(
        "Faça upload do modelo (.pkl)",
        type=['pkl'],
        help="Arquivo .pkl gerado pelo código acima"
    )

    if uploaded_file:
        try:
            # Salva o arquivo
            with open('modelo_viabilidade_final.pkl', 'wb') as f:
                f.write(uploaded_file.read())

            st.success("✅ Modelo carregado com sucesso!")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao carregar modelo: {e}")