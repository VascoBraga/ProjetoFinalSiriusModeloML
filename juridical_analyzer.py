"""
Classe principal para análise de viabilidade jurídica
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import warnings
warnings.filterwarnings('ignore')

class JuridicalAnalyzer:
    """Classe principal para análise de viabilidade jurídica"""

    def __init__(self):
        self.model = None
        self.feature_names = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Carrega o modelo treinado"""
        try:
            with open('modelo_viabilidade_final.pkl', 'rb') as f:
                model_data = pickle.load(f)
                self.model = model_data['model']
                self.feature_names = model_data['feature_names']
                self.scaler = model_data.get('scaler', None)

            st.session_state['model_loaded'] = True

        except FileNotFoundError:
            st.session_state['model_loaded'] = False
            st.warning("⚠️ Modelo não encontrado! Treine o modelo primeiro.")

    def create_features_from_input(self, input_data):
        """Cria features a partir dos dados de entrada"""
        
        # Inicializa DataFrame com zeros
        features_df = pd.DataFrame(0, index=[0], columns=self.feature_names)

        # 1. REGIÃO/UF
        uf = input_data.get('uf', '')
        if f'uf_{uf}' in features_df.columns:
            features_df[f'uf_{uf}'] = 1

        regiao = input_data.get('regiao', '')
        if f'regiao_{regiao}' in features_df.columns:
            features_df[f'regiao_{regiao}'] = 1

        # 2. VALOR
        valor = input_data.get('valor_causa', 0)
        if 'ValorCausa' in features_df.columns:
            features_df['ValorCausa'] = valor

        if 'valor_log' in features_df.columns:
            features_df['valor_log'] = np.log1p(valor)

        # Faixas de valor
        if valor <= 2000:
            if 'valor_baixo' in features_df.columns:
                features_df['valor_baixo'] = 1
        elif valor <= 4000:
            if 'valor_medio' in features_df.columns:
                features_df['valor_medio'] = 1
        else:
            if 'valor_alto' in features_df.columns:
                features_df['valor_alto'] = 1

        # 3. CONFIANÇA
        confianca = input_data.get('confianca', 0.7)
        if 'ValorCausaConfianca' in features_df.columns:
            features_df['ValorCausaConfianca'] = confianca

        if 'valor_x_confianca' in features_df.columns:
            features_df['valor_x_confianca'] = valor * confianca

        # 4. DADOS DEMOGRÁFICOS
        sexo = input_data.get('sexo', 'M')
        if f'sexo_{sexo}' in features_df.columns:
            features_df[f'sexo_{sexo}'] = 1

        faixa_etaria = input_data.get('faixa_etaria', 3)
        if 'faixa_etaria_num' in features_df.columns:
            features_df['faixa_etaria_num'] = faixa_etaria

        # Grupos de idade
        if faixa_etaria <= 2 and 'idade_jovem' in features_df.columns:
            features_df['idade_jovem'] = 1
        elif 3 <= faixa_etaria <= 5 and 'idade_adulto' in features_df.columns:
            features_df['idade_adulto'] = 1
        elif faixa_etaria >= 6 and 'idade_senior' in features_df.columns:
            features_df['idade_senior'] = 1

        # 5. ANO
        ano = input_data.get('ano', 2024)
        if f'ano_{ano}' in features_df.columns:
            features_df[f'ano_{ano}'] = 1

        # 6. TIPO DE ASSUNTO/PROBLEMA
        tipo_assunto = input_data.get('tipo_assunto', '')
        
        # Mapeia tipos para códigos de assunto
        assunto_mapping = {
            'Telefonia/Internet': [1, 2, 3],
            'Bancos/Financeiro': [4, 5, 6],
            'Energia Elétrica': [7],
            'Comércio/Produto': [8, 9, 10],
            'Plano de Saúde': [11],
            'Transporte Aéreo': [12],
            'Outros': [99]
        }

        if tipo_assunto in assunto_mapping:
            codigo = assunto_mapping[tipo_assunto][0]
            if f'assunto_{codigo}' in features_df.columns:
                features_df[f'assunto_{codigo}'] = 1

        return features_df

    def predict_viability(self, input_data):
        """Faz predição de viabilidade"""
        
        if not self.model:
            return None

        # Cria features
        features_df = self.create_features_from_input(input_data)

        # Escala se necessário
        if self.scaler:
            features_scaled = self.scaler.transform(features_df)
            features_df = pd.DataFrame(features_scaled, columns=self.feature_names)

        # Predição
        try:
            probability = self.model.predict_proba(features_df)[0]
            prediction = self.model.predict(features_df)[0]

            return {
                'prediction': prediction,
                'probability_nao_viavel': probability[0],
                'probability_viavel': probability[1],
                'confidence': max(probability)
            }

        except Exception as e:
            st.error(f"Erro na predição: {e}")
            return None

@st.cache_resource
def load_analyzer():
    """Carrega e cacheia o analyzer"""
    return JuridicalAnalyzer()