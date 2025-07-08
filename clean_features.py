"""
Módulo para criação de features limpas (sem data leakage)
"""

import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold

from config import FEATURES_PROIBIDAS, DEFAULT_CONFIG
from data_preparation import (
    criar_features_geograficas, criar_features_demograficas,
    criar_features_valor, criar_features_temporais, criar_features_codigo
)


def criar_features_limpas(df_balanced):
    """
    Cria dataset de features SEM vazamento de dados
    
    Args:
        df_balanced: DataFrame balanceado
        
    Returns:
        pd.DataFrame: DataFrame sem features problemáticas
    """
    print("🧹 CRIANDO FEATURES LIMPAS (SEM DATA LEAKAGE)")
    print("=" * 50)
    
    df_clean = df_balanced.copy()
    
    print("📋 Features a serem removidas:")
    features_removidas = []
    for col in FEATURES_PROIBIDAS:
        if col in df_clean.columns:
            features_removidas.append(col)
            print(f"  ❌ {col}")
    
    # Remove features proibidas
    df_clean = df_clean.drop(columns=features_removidas)
    
    print(f"\n✅ {len(features_removidas)} features removidas")
    print(f"📊 Shape após limpeza: {df_clean.shape}")
    
    return df_clean


def criar_features_text_independentes(df_clean):
    """
    Cria features de texto de forma independente (sem usar target)
    
    Args:
        df_clean: DataFrame limpo
        
    Returns:
        pd.DataFrame: DataFrame com features independentes
    """
    print("\n📝 CRIANDO FEATURES DE TEXTO INDEPENDENTES")
    print("=" * 45)
    
    # 1. FEATURES GEOGRÁFICAS
    df_clean = criar_features_geograficas(df_clean)
    
    # 2. FEATURES DEMOGRÁFICAS
    df_clean = criar_features_demograficas(df_clean)
    
    # 3. FEATURES DE VALOR
    df_clean = criar_features_valor(df_clean)
    
    # 4. FEATURES TEMPORAIS
    df_clean = criar_features_temporais(df_clean)
    
    # 5. FEATURES DE CÓDIGO/CATEGORIA
    df_clean = criar_features_codigo(df_clean)
    
    # Remove colunas categóricas originais para evitar problemas
    cols_remover = ['Regiao', 'UF', 'SexoConsumidor', 'FaixaEtariaConsumidor', 
                   'CodigoAssunto', 'CodigoProblema']
    df_clean = df_clean.drop(columns=[col for col in cols_remover if col in df_clean.columns])
    
    print(f"✅ Features de texto independentes criadas")
    print(f"📊 Shape final: {df_clean.shape}")
    
    return df_clean


def preparar_dados_limpos(df_balanced):
    """
    Prepara dados completamente limpos para ML
    
    Args:
        df_balanced: DataFrame balanceado
        
    Returns:
        tuple: (X_final, y, feature_names)
    """
    print("🎯 PREPARANDO DADOS LIMPOS PARA ML")
    print("=" * 40)
    
    # 1. Limpeza inicial
    df_clean = criar_features_limpas(df_balanced)
    
    # 2. Features independentes
    df_features = criar_features_text_independentes(df_clean)
    
    # 3. Separar target
    if 'Viavel' not in df_balanced.columns:
        print("❌ Coluna 'Viavel' não encontrada!")
        return None, None, None
    
    # Target vem do dataset original
    y = df_balanced['Viavel'].copy()
    
    # Features finais (apenas numéricas)
    feature_cols = df_features.select_dtypes(include=[np.number]).columns.tolist()
    X = df_features[feature_cols].copy()
    
    # Limpeza final
    X = X.fillna(0)
    X = X.replace([np.inf, -np.inf], 0)
    
    # Remove features com variância zero
    selector = VarianceThreshold(threshold=DEFAULT_CONFIG['variance_threshold'])
    X_filtered = selector.fit_transform(X)
    
    feature_names = X.columns[selector.get_support()].tolist()
    X_final = pd.DataFrame(X_filtered, columns=feature_names, index=X.index)
    
    print(f"✅ Dados limpos preparados:")
    print(f"   Features: {X_final.shape[1]}")
    print(f"   Amostras: {X_final.shape[0]}")
    print(f"   Distribuição target: {y.value_counts().to_dict()}")
    
    print(f"\n📋 FEATURES FINAIS:")
    for i, feature in enumerate(feature_names):
        print(f"  {i+1:2d}. {feature}")
    
    return X_final, y, feature_names