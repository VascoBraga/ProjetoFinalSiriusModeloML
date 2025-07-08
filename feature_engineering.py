"""
Módulo para feature engineering especializado em classificação de viabilidade jurídica.
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder, StandardScaler
from config import PALAVRAS_JURIDICAS, STOPWORDS_PORTUGUES, MAX_FEATURES_TFIDF, MIN_DF, MAX_DF


class ViabilidadeFeatureEngineer:
    """
    Feature Engineering especializado para classificação de viabilidade de causas jurídicas
    """

    def __init__(self):
        self.vectorizer_assunto = None
        self.vectorizer_problema = None
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.palavras_juridicas = PALAVRAS_JURIDICAS

    def extrair_features_texto(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extrai features específicas dos campos de texto
        """
        print("📝 EXTRAINDO FEATURES DE TEXTO")
        print("-" * 40)

        df_features = df.copy()

        # 1. FEATURES BÁSICAS DE TEXTO
        print("1️⃣ Features básicas de texto...")

        # Comprimento dos textos
        df_features['assunto_length'] = df_features['DescricaoAssunto'].str.len()
        df_features['problema_length'] = df_features['DescricaoProblema'].str.len()
        df_features['texto_total_length'] = df_features['assunto_length'] + df_features['problema_length']

        # Contagem de palavras
        df_features['assunto_words'] = df_features['DescricaoAssunto'].str.split().str.len()
        df_features['problema_words'] = df_features['DescricaoProblema'].str.split().str.len()
        df_features['texto_total_words'] = df_features['assunto_words'] + df_features['problema_words']

        # 2. FEATURES ESPECÍFICAS DO DOMÍNIO JURÍDICO
        print("2️⃣ Features específicas do domínio jurídico...")

        # Combina textos para análise
        df_features['texto_completo'] = (
            df_features['DescricaoAssunto'].fillna('') + ' ' +
            df_features['DescricaoProblema'].fillna('')
        ).str.lower()

        # Conta palavras-chave por categoria
        for categoria, palavras in self.palavras_juridicas.items():
            df_features[f'count_{categoria}'] = df_features['texto_completo'].apply(
                lambda x: sum(1 for palavra in palavras if palavra in x)
            )

        # 3. FEATURES DE GRAVIDADE E URGÊNCIA
        print("3️⃣ Features de gravidade e urgência...")

        # Score de gravidade (combinado)
        df_features['score_gravidade'] = (
            df_features['count_gravidade_alta'] * 3 +
            df_features['count_alta_viabilidade'] * 2 +
            df_features['count_complexidade_alta'] * 1
        )

        # Score de viabilidade textual
        df_features['score_viabilidade_texto'] = (
            df_features['count_alta_viabilidade'] * 2 +
            df_features['count_setores_viaveis'] * 1 +
            df_features['count_jurisprudencia_consolidada'] * 1 -
            df_features['count_baixa_viabilidade'] * 2
        )

        # 4. FEATURES DE TIPO DE PROBLEMA
        print("4️⃣ Features de categorização...")

        # Detecta tipos principais de problema
        df_features['is_dano_moral'] = df_features['texto_completo'].str.contains('dano moral|constrangimento|humilhação').astype(int)
        df_features['is_cobranca_indevida'] = df_features['texto_completo'].str.contains('cobrança indevida|valor indevido').astype(int)
        df_features['is_produto_defeituoso'] = df_features['texto_completo'].str.contains('defeito|vício|quebrado|não funciona').astype(int)
        df_features['is_servico_nao_prestado'] = df_features['texto_completo'].str.contains('não prestado|não entregue|não fornecido').astype(int)
        df_features['is_negativacao'] = df_features['texto_completo'].str.contains('negativação|spc|serasa|protesto').astype(int)

        # 5. FEATURES DE EMPRESA/SETOR
        print("5️⃣ Features de empresa/setor...")

        # Detecta setores principais
        df_features['is_setor_financeiro'] = df_features['texto_completo'].str.contains('banco|cartão|empréstimo|financiamento').astype(int)
        df_features['is_setor_telecom'] = df_features['texto_completo'].str.contains('telefon|internet|banda larga|celular').astype(int)
        df_features['is_setor_energia'] = df_features['texto_completo'].str.contains('energia|luz|eletricidade').astype(int)
        df_features['is_setor_saude'] = df_features['texto_completo'].str.contains('saúde|médico|convênio|hospital').astype(int)
        df_features['is_setor_transporte'] = df_features['texto_completo'].str.contains('aéreo|voo|ônibus|transporte').astype(int)

        print(f"✅ {len([col for col in df_features.columns if col not in df.columns])} features de texto criadas")

        return df_features

    def processar_texto_avancado(self, df: pd.DataFrame, max_features: int = MAX_FEATURES_TFIDF) -> pd.DataFrame:
        """
        Processa texto usando TF-IDF para capturar padrões mais complexos
        """
        print("🔍 PROCESSAMENTO AVANÇADO DE TEXTO (TF-IDF)")
        print("-" * 45)

        df_resultado = df.copy()

        # Prepara textos
        textos_assunto = df['DescricaoAssunto'].fillna('').str.lower()
        textos_problema = df['DescricaoProblema'].fillna('').str.lower()

        # 1. TF-IDF para Assuntos
        print("1️⃣ TF-IDF para assuntos...")

        self.vectorizer_assunto = TfidfVectorizer(
            max_features=max_features//2,
            stop_words=STOPWORDS_PORTUGUES,
            ngram_range=(1, 2),
            min_df=MIN_DF,
            max_df=MAX_DF
        )

        tfidf_assunto = self.vectorizer_assunto.fit_transform(textos_assunto)

        # Adiciona features TF-IDF do assunto
        for i, feature_name in enumerate(self.vectorizer_assunto.get_feature_names_out()):
            df_resultado[f'assunto_tfidf_{feature_name}'] = tfidf_assunto[:, i].toarray().flatten()

        # 2. TF-IDF para Problemas
        print("2️⃣ TF-IDF para problemas...")

        self.vectorizer_problema = TfidfVectorizer(
            max_features=max_features//2,
            stop_words=STOPWORDS_PORTUGUES,
            ngram_range=(1, 2),
            min_df=MIN_DF,
            max_df=MAX_DF
        )

        tfidf_problema = self.vectorizer_problema.fit_transform(textos_problema)

        # Adiciona features TF-IDF do problema
        for i, feature_name in enumerate(self.vectorizer_problema.get_feature_names_out()):
            df_resultado[f'problema_tfidf_{feature_name}'] = tfidf_problema[:, i].toarray().flatten()

        print(f"✅ {tfidf_assunto.shape[1] + tfidf_problema.shape[1]} features TF-IDF criadas")

        return df_resultado

    def criar_features_categoricas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria features categóricas específicas para o problema
        """
        print("🏷️ CRIANDO FEATURES CATEGÓRICAS")
        print("-" * 35)

        df_features = df.copy()

        # 1. ENCODING DE VARIÁVEIS CATEGÓRICAS EXISTENTES
        print("1️⃣ Encoding de variáveis existentes...")

        # UF - One-Hot Encoding (limitado aos principais)
        principais_ufs = df['UF'].value_counts().head(10).index.tolist()
        for uf in principais_ufs:
            df_features[f'uf_{uf}'] = (df_features['UF'] == uf).astype(int)

        # Região - Label Encoding
        if 'Regiao' in df.columns:
            le_regiao = LabelEncoder()
            df_features['regiao_encoded'] = le_regiao.fit_transform(df_features['Regiao'].fillna('Desconhecida'))
            self.label_encoders['Regiao'] = le_regiao

        # Sexo e Faixa Etária
        if 'SexoConsumidor' in df.columns:
            df_features['sexo_M'] = (df_features['SexoConsumidor'] == 'M').astype(int)
            df_features['sexo_F'] = (df_features['SexoConsumidor'] == 'F').astype(int)

        if 'FaixaEtariaConsumidor' in df.columns:
            # Cria variáveis dummy para faixas etárias
            faixas_etarias = df_features['FaixaEtariaConsumidor'].unique()
            for faixa in faixas_etarias:
                if pd.notna(faixa):
                    df_features[f'idade_{faixa.replace(" ", "_")}'] = (df_features['FaixaEtariaConsumidor'] == faixa).astype(int)

        # Atendida
        if 'Atendida' in df.columns:
            df_features['foi_atendida'] = (df_features['Atendida'] == 'S').astype(int)

        # 2. FEATURES DERIVADAS DE CNPJ/EMPRESA
        print("2️⃣ Features de empresa...")

        if 'NumeroCNPJ' in df.columns:
            # Porte da empresa baseado no CNPJ (simplificado)
            df_features['cnpj_length'] = df_features['NumeroCNPJ'].astype(str).str.len()
            df_features['is_grande_empresa'] = (df_features['cnpj_length'] >= 14).astype(int)

        # 3. FEATURES TEMPORAIS
        print("3️⃣ Features temporais...")

        if 'DataAbertura' in df.columns:
            # Converte para datetime se necessário
            df_features['DataAbertura'] = pd.to_datetime(df_features['DataAbertura'], errors='coerce')

            # Extrai componentes temporais
            df_features['mes_abertura'] = df_features['DataAbertura'].dt.month
            df_features['trimestre_abertura'] = df_features['DataAbertura'].dt.quarter
            df_features['dia_semana_abertura'] = df_features['DataAbertura'].dt.dayofweek

            # Features sazonais
            df_features['is_inicio_ano'] = (df_features['mes_abertura'] <= 3).astype(int)
            df_features['is_fim_ano'] = (df_features['mes_abertura'] >= 10).astype(int)

        print(f"✅ Features categóricas criadas")

        return df_features

    def criar_features_numericas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria e transforma features numéricas
        """
        print("🔢 CRIANDO FEATURES NUMÉRICAS")
        print("-" * 30)

        df_features = df.copy()

        # 1. TRANSFORMAÇÕES DE VALOR
        print("1️⃣ Transformações de valor...")

        # Log do valor (para lidar com distribuição assimétrica)
        df_features['valor_causa_log'] = np.log1p(df_features['ValorCausa'].fillna(0))

        # Faixas de valor
        df_features['faixa_valor'] = pd.cut(
            df_features['ValorCausa'].fillna(0),
            bins=[0, 1000, 3000, 5000, 10000, 20000, float('inf')],
            labels=['muito_baixo', 'baixo', 'medio', 'alto', 'muito_alto', 'extremo']
        )

        # One-hot para faixas de valor
        for faixa in ['muito_baixo', 'baixo', 'medio', 'alto', 'muito_alto', 'extremo']:
            df_features[f'valor_{faixa}'] = (df_features['faixa_valor'] == faixa).astype(int)

        # 2. FEATURES DE CONFIABILIDADE
        print("2️⃣ Features de confiabilidade...")

        if 'ValorCausaConfianca' in df.columns:
            # Faixas de confiança
            df_features['alta_confianca'] = (df_features['ValorCausaConfianca'] >= 0.8).astype(int)
            df_features['media_confianca'] = ((df_features['ValorCausaConfianca'] >= 0.5) & (df_features['ValorCausaConfianca'] < 0.8)).astype(int)
            df_features['baixa_confianca'] = (df_features['ValorCausaConfianca'] < 0.5).astype(int)

        # 3. FEATURES DE SCORES (se disponível)
        print("3️⃣ Features de scores...")

        score_columns = [col for col in df.columns if col.startswith('Score_')]
        if score_columns:
            # Normaliza scores
            for col in score_columns:
                df_features[f'{col}_normalized'] = df_features[col] / df_features[col].max()

            # Score total como percentual
            if 'Score_Total' in df.columns:
                df_features['score_total_percent'] = df_features['Score_Total'] / 10  # Assumindo máximo 10

        print(f"✅ Features numéricas criadas")

        return df_features

    def executar_feature_engineering_completo(self, df: pd.DataFrame,
                                            incluir_tfidf: bool = True,
                                            max_features_tfidf: int = MAX_FEATURES_TFIDF) -> pd.DataFrame:
        """
        Executa feature engineering completo
        """
        print("🚀 FEATURE ENGINEERING COMPLETO")
        print("=" * 50)

        print(f"📊 DataFrame inicial: {df.shape}")

        # 1. Features de texto básicas
        df_result = self.extrair_features_texto(df)
        print(f"📊 Após features de texto: {df_result.shape}")

        # 2. Features categóricas
        df_result = self.criar_features_categoricas(df_result)
        print(f"📊 Após features categóricas: {df_result.shape}")

        # 3. Features numéricas
        df_result = self.criar_features_numericas(df_result)
        print(f"📊 Após features numéricas: {df_result.shape}")

        # 4. TF-IDF (opcional - pode ser pesado)
        if incluir_tfidf and len(df) <= 10000:  # Só para datasets menores
            print("⚠️ TF-IDF incluído - pode ser lento para datasets grandes")
            df_result = self.processar_texto_avancado(df_result, max_features_tfidf)
            print(f"📊 Após TF-IDF: {df_result.shape}")
        elif incluir_tfidf:
            print("⚠️ TF-IDF pulado - dataset muito grande. Use incluir_tfidf=False")

        # 5. Limpeza final
        print("🧹 Limpeza final...")

        # Remove colunas auxiliares
        colunas_remover = ['texto_completo', 'faixa_valor']
        df_result = df_result.drop(columns=[col for col in colunas_remover if col in df_result.columns])

        # Converte booleanos para int
        bool_cols = df_result.select_dtypes(include=['bool']).columns
        df_result[bool_cols] = df_result[bool_cols].astype(int)

        print(f"✅ FEATURE ENGINEERING CONCLUÍDO!")
        print(f"📊 Shape final: {df_result.shape}")
        print(f"🎯 Features criadas: {df_result.shape[1] - df.shape[1]}")

        return df_result

    def preparar_para_ml(self, df_features: pd.DataFrame, target_col: str = 'Viavel') -> tuple:
        """
        Prepara dados para machine learning
        """
        print("🤖 PREPARANDO PARA MACHINE LEARNING")
        print("-" * 35)

        # Separa features e target
        if target_col not in df_features.columns:
            print(f"❌ Coluna target '{target_col}' não encontrada!")
            return None, None, None

        X = df_features.drop(columns=[target_col])
        y = df_features[target_col]

        # Remove colunas de texto originais e outras não necessárias
        from config import COLUNAS_REMOVER_ML
        X = X.drop(columns=[col for col in COLUNAS_REMOVER_ML if col in X.columns])

        # Converte categóricas restantes para numéricas
        for col in X.select_dtypes(include=['object']).columns:
            if X[col].nunique() < 50:  # Só se poucos valores únicos
                X[col] = LabelEncoder().fit_transform(X[col].astype(str))
            else:
                X = X.drop(columns=[col])  # Remove se muitos valores únicos

        # Trata valores infinitos e NaN
        X = X.replace([np.inf, -np.inf], np.nan)
        X = X.fillna(0)

        print(f"✅ Preparação concluída:")
        print(f"   Features (X): {X.shape}")
        print(f"   Target (y): {y.shape}")
        print(f"   Distribuição do target: {y.value_counts().to_dict()}")

        feature_names = X.columns.tolist()

        return X, y, feature_names


def executar_feature_engineering(df_com_target: pd.DataFrame,
                                incluir_tfidf: bool = False) -> pd.DataFrame:
    """
    Função principal para executar feature engineering

    Args:
        df_com_target: DataFrame com target criado
        incluir_tfidf: Se incluir features TF-IDF (lento para datasets grandes)

    Returns:
        DataFrame com features para ML
    """
    print("🎯 EXECUTANDO FEATURE ENGINEERING PARA ML")
    print("=" * 55)

    # Inicializa feature engineer
    fe = ViabilidadeFeatureEngineer()

    # Executa feature engineering
    df_features = fe.executar_feature_engineering_completo(
        df_com_target,
        incluir_tfidf=incluir_tfidf
    )

    return df_features