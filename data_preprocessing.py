"""
Módulo para preprocessamento e limpeza de dados do SINDEC.
"""

import pandas as pd
import numpy as np
from config import COLUNAS_VALOR_CAUSA


def limpar_coluna_atendida(df):
    """
    Limpa a coluna 'Atendida' mantendo apenas valores válidos
    """
    print("🧹 LIMPANDO COLUNA 'ATENDIDA'")
    print(f"Valores únicos antes: {df['Atendida'].nunique()}")
    print(f"Distribuição antes:\n{df['Atendida'].value_counts()}")

    # Mapeia apenas valores válidos
    df['Atendida_Original'] = df['Atendida'].copy()  # Backup

    # Limpa: mantém apenas S, N, ou converte para NaN
    valores_validos = ['S', 'N']
    df['Atendida'] = df['Atendida'].where(
        df['Atendida'].isin(valores_validos),
        np.nan
    )

    # Estatísticas pós-limpeza
    print(f"\n✅ Valores únicos após limpeza: {df['Atendida'].nunique()}")
    print(f"Distribuição após:\n{df['Atendida'].value_counts()}")
    print(f"Valores perdidos: {df['Atendida'].isna().sum()} ({df['Atendida'].isna().mean():.1%})")

    return df


def verificar_valores_nulos_causa(df):
    """
    Verifica valores nulos nas colunas de valor de causa
    """
    print("🔍 VERIFICANDO VALORES NULOS NAS COLUNAS DE VALOR DE CAUSA")
    
    valores_nulos_por_coluna = df[COLUNAS_VALOR_CAUSA].isnull().sum()
    
    print("Contagem de valores nulos por coluna:")
    print(valores_nulos_por_coluna)
    
    algum_nulo = valores_nulos_por_coluna.sum() > 0
    
    if algum_nulo:
        print("\nSim, existem valores nulos em uma ou mais colunas de valor de causa estimadas.")
    else:
        print("\nNão, não existem valores nulos nas colunas de valor de causa estimadas.")
    
    return valores_nulos_por_coluna


def preprocessar_dados(df):
    """
    Executa preprocessamento completo dos dados
    """
    print("🚀 INICIANDO PREPROCESSAMENTO DOS DADOS")
    print("=" * 50)
    
    # Cópia do dataframe
    df_processado = df.copy()
    
    # Verificar valores nulos
    verificar_valores_nulos_causa(df_processado)
    
    # Limpar coluna Atendida
    df_processado = limpar_coluna_atendida(df_processado)
    
    # Remover registros com Atendida nulo
    df_processado = df_processado.dropna(subset=['Atendida'])
    print(f"Total de linhas após remover registros com 'Atendida' nulo: {len(df_processado)}")
    
    print("\n✅ PREPROCESSAMENTO CONCLUÍDO")
    
    return df_processado