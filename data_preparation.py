"""
Módulo para preparação de dados para balanceamento
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from config import NUMERIC_FEATURES, DEFAULT_CONFIG


def preparar_dados_para_balanceamento(df_com_target):
    """
    Prepara os dados do SINDEC para balanceamento
    
    Args:
        df_com_target: DataFrame com target de viabilidade
        
    Returns:
        tuple: (X, y, available_features)
    """
    print("🔧 PREPARANDO DADOS PARA BALANCEAMENTO")
    print("=" * 45)
    
    # Remove registros com target missing
    df_clean = df_com_target.dropna(subset=['Viavel']).copy()
    print(f"📊 Registros após limpeza: {len(df_clean):,}")
    
    # Seleciona features numéricas relevantes
    numeric_features = NUMERIC_FEATURES.copy()
    
    # Adiciona features categóricas encodadas
    categorical_encoded = []
    
    # Encoding simples para UF (top 10)
    top_ufs = df_clean['UF'].value_counts().head(DEFAULT_CONFIG['top_ufs']).index
    for uf in top_ufs:
        col_name = f'UF_{uf}'
        df_clean[col_name] = (df_clean['UF'] == uf).astype(int)
        categorical_encoded.append(col_name)
    
    # Encoding para região
    if 'Regiao' in df_clean.columns:
        le_regiao = LabelEncoder()
        df_clean['Regiao_encoded'] = le_regiao.fit_transform(df_clean['Regiao'].fillna('Desconhecida'))
        categorical_encoded.append('Regiao_encoded')
    
    # Lista final de features
    all_features = numeric_features + categorical_encoded
    
    # Verifica quais features existem no DataFrame
    available_features = [col for col in all_features if col in df_clean.columns]
    
    print(f"📋 Features selecionadas: {len(available_features)}")
    for feature in available_features:
        print(f"   ✓ {feature}")
    
    # Prepara X e y
    X = df_clean[available_features].copy()
    y = df_clean['Viavel'].copy()
    
    # Tratamento de valores missing e problemáticos
    X = X.fillna(0)
    X = X.replace([np.inf, -np.inf], 0)
    
    print(f"\n📊 Shape final: X={X.shape}, y={y.shape}")
    print(f"🎯 Distribuição target original:")
    print(f"   Não Viável (0): {(y==0).sum():,} ({(y==0).mean()*100:.1f}%)")
    print(f"   Viável (1): {(y==1).sum():,} ({(y==1).mean()*100:.1f}%)")
    
    return X, y, available_features


def criar_features_geograficas(df_clean):
    """Cria features geográficas"""
    print("1️⃣ Features geográficas...")
    
    # Região encoding
    if 'Regiao' in df_clean.columns:
        regiao_dummies = pd.get_dummies(df_clean['Regiao'], prefix='regiao')
        df_clean = pd.concat([df_clean, regiao_dummies], axis=1)
    
    # UF - apenas os principais
    if 'UF' in df_clean.columns:
        principais_ufs = df_clean['UF'].value_counts().head(DEFAULT_CONFIG['top_ufs']).index
        for uf in principais_ufs:
            df_clean[f'uf_{uf}'] = (df_clean['UF'] == uf).astype(int)
    
    return df_clean


def criar_features_demograficas(df_clean):
    """Cria features demográficas"""
    print("2️⃣ Features demográficas...")
    
    if 'SexoConsumidor' in df_clean.columns:
        df_clean['sexo_M'] = (df_clean['SexoConsumidor'] == 'M').astype(int)
        df_clean['sexo_F'] = (df_clean['SexoConsumidor'] == 'F').astype(int)
    
    if 'FaixaEtariaConsumidor' in df_clean.columns:
        from config import FAIXA_ETARIA_MAP
        
        # Simplifica faixas etárias
        df_clean['faixa_etaria_num'] = df_clean['FaixaEtariaConsumidor'].map(FAIXA_ETARIA_MAP).fillna(0)
        
        # Grupos de idade
        df_clean['idade_jovem'] = (df_clean['faixa_etaria_num'] <= 2).astype(int)
        df_clean['idade_adulto'] = ((df_clean['faixa_etaria_num'] >= 3) & 
                                   (df_clean['faixa_etaria_num'] <= 5)).astype(int)
        df_clean['idade_senior'] = (df_clean['faixa_etaria_num'] >= 6).astype(int)
    
    return df_clean


def criar_features_valor(df_clean):
    """Cria features de valor"""
    print("3️⃣ Features de valor...")
    
    if 'ValorCausa' in df_clean.columns:
        # Log do valor
        df_clean['valor_log'] = np.log1p(df_clean['ValorCausa'])
        
        # Faixas de valor
        quartis = df_clean['ValorCausa'].quantile([0.25, 0.5, 0.75])
        df_clean['valor_baixo'] = (df_clean['ValorCausa'] <= quartis[0.25]).astype(int)
        df_clean['valor_medio'] = ((df_clean['ValorCausa'] > quartis[0.25]) &
                                  (df_clean['ValorCausa'] <= quartis[0.75])).astype(int)
        df_clean['valor_alto'] = (df_clean['ValorCausa'] > quartis[0.75]).astype(int)
        
        # Interação valor x confiança
        if 'ValorCausaConfianca' in df_clean.columns:
            df_clean['valor_x_confianca'] = df_clean['ValorCausa'] * df_clean['ValorCausaConfianca']
    
    return df_clean


def criar_features_temporais(df_clean):
    """Cria features temporais"""
    print("4️⃣ Features temporais...")
    
    if 'AnoCalendario' in df_clean.columns:
        # Anos como categórica
        for ano in df_clean['AnoCalendario'].unique():
            if pd.notna(ano):
                df_clean[f'ano_{int(ano)}'] = (df_clean['AnoCalendario'] == ano).astype(int)
    
    return df_clean


def criar_features_codigo(df_clean):
    """Cria features de código/categoria"""
    print("5️⃣ Features de código...")
    
    # Códigos de assunto (agrupados)
    if 'CodigoAssunto' in df_clean.columns:
        principais_assuntos = df_clean['CodigoAssunto'].value_counts().head(DEFAULT_CONFIG['top_assuntos']).index
        for codigo in principais_assuntos:
            if pd.notna(codigo):
                df_clean[f'assunto_{codigo}'] = (df_clean['CodigoAssunto'] == codigo).astype(int)
    
    return df_clean