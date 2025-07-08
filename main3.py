"""
Arquivo principal para execução do algoritmo de classificação SINDEC
"""

import pandas as pd
import sys
import os

# Importa módulos locais
from balancing import aplicar_balanceamento_sindec
from model_training import treinar_modelo_limpo, selecionar_melhor_modelo
from config import DEFAULT_CONFIG


def executar_pipeline_completo(df_com_target, strategy='moderate', run_analysis=True):
    """
    Executa o pipeline completo de balanceamento e treinamento
    
    Args:
        df_com_target: DataFrame com target de viabilidade
        strategy: Estratégia de balanceamento
        run_analysis: Se deve executar análise completa
        
    Returns:
        dict: Resultados do pipeline completo
    """
    print("🚀 INICIANDO PIPELINE COMPLETO DE CLASSIFICAÇÃO SINDEC")
    print("=" * 65)
    
    # 1. Aplicar balanceamento
    print("\n📊 ETAPA 1: BALANCEAMENTO DE DADOS")
    print("=" * 40)
    
    df_balanced, balancing_results = aplicar_balanceamento_sindec(
        df_com_target, 
        strategy=strategy, 
        run_analysis=run_analysis
    )
    
    if df_balanced is None:
        print("❌ Erro no balanceamento. Abortando pipeline.")
        return None
    
    # 2. Treinar modelos limpos
    print("\n🤖 ETAPA 2: TREINAMENTO DE MODELOS")
    print("=" * 40)
    
    model_results, X_train, X_test, y_train, y_test, feature_names = treinar_modelo_limpo(df_balanced)
    
    if model_results is None:
        print("❌ Erro no treinamento. Abortando pipeline.")
        return None
    
    # 3. Selecionar melhor modelo
    nome_melhor, melhor_modelo, melhor_score = selecionar_melhor_modelo(model_results)
    
    # 4. Preparar resultados finais
    resultados_finais = {
        'balancing': balancing_results,
        'models': model_results,
        'best_model': {
            'name': nome_melhor,
            'model': melhor_modelo,
            'score': melhor_score
        },
        'data': {
            'df_balanced': df_balanced,
            'X_train': X_train,
            'X_test': X_test,
            'y_train': y_train,
            'y_test': y_test,
            'feature_names': feature_names
        }
    }
    
    print("\n✅ PIPELINE CONCLUÍDO COM SUCESSO!")
    print(f"🏆 Melhor modelo: {nome_melhor} (AUC: {melhor_score:.3f})")
    
    return resultados_finais


def executar_pipeline_simples(df_com_target, strategy='moderate'):
    """
    Executa pipeline simplificado (mais rápido)
    
    Args:
        df_com_target: DataFrame com target
        strategy: Estratégia de balanceamento
        
    Returns:
        dict: Resultados simplificados
    """
    print("⚡ PIPELINE SIMPLIFICADO")
    print("=" * 25)
    
    # Balanceamento sem análise completa
    df_balanced, _ = aplicar_balanceamento_sindec(
        df_com_target, 
        strategy=strategy, 
        run_analysis=False
    )
    
    if df_balanced is None:
        return None
    
    # Treinamento direto
    model_results, X_train, X_test, y_train, y_test, feature_names = treinar_modelo_limpo(df_balanced)
    
    if model_results is None:
        return None
    
    # Selecionar melhor modelo
    nome_melhor, melhor_modelo, melhor_score = selecionar_melhor_modelo(model_results)
    
    return {
        'df_balanced': df_balanced,
        'best_model': melhor_modelo,
        'best_model_name': nome_melhor,
        'best_score': melhor_score,
        'X_test': X_test,
        'y_test': y_test,
        'feature_names': feature_names
    }


def salvar_modelo_final(modelo, feature_names, nome_arquivo='modelo_sindec_final.pkl'):
    """
    Salva o modelo final treinado
    
    Args:
        modelo: Modelo treinado
        feature_names: Lista de nomes das features
        nome_arquivo: Nome do arquivo para salvar
    """
    import pickle
    
    modelo_data = {
        'model': modelo,
        'feature_names': feature_names,
        'config': DEFAULT_CONFIG
    }
    
    with open(nome_arquivo, 'wb') as f:
        pickle.dump(modelo_data, f)
    
    print(f"💾 Modelo salvo em: {nome_arquivo}")


def carregar_modelo_final(nome_arquivo='modelo_sindec_final.pkl'):
    """
    Carrega modelo salvo
    
    Args:
        nome_arquivo: Nome do arquivo do modelo
        
    Returns:
        dict: Dados do modelo carregado
    """
    import pickle
    
    try:
        with open(nome_arquivo, 'rb') as f:
            modelo_data = pickle.load(f)
        
        print(f"📂 Modelo carregado de: {nome_arquivo}")
        return modelo_data
    
    except FileNotFoundError:
        print(f"❌ Arquivo {nome_arquivo} não encontrado!")
        return None


def fazer_predicao(modelo_data, dados_novos):
    """
    Faz predição com modelo carregado
    
    Args:
        modelo_data: Dados do modelo carregado
        dados_novos: DataFrame com novos dados
        
    Returns:
        array: Predições
    """
    modelo = modelo_data['model']
    feature_names = modelo_data['feature_names']
    
    # Seleciona apenas as features usadas no treinamento
    X_pred = dados_novos[feature_names]
    
    # Faz predições
    predicoes = modelo.predict(X_pred)
    probabilidades = modelo.predict_proba(X_pred)[:, 1]
    
    return predicoes, probabilidades


if __name__ == "__main__":
    print("🎯 ALGORITMO DE CLASSIFICAÇÃO SINDEC")
    print("=" * 40)
    print("📝 Para usar este módulo:")
    print("   1. Importe o módulo")
    print("   2. Carregue seus dados com target criado")
    print("   3. Execute o pipeline:")
    print()
    print("   # Pipeline completo (com análise)")
    print("   resultados = executar_pipeline_completo(df_com_target)")
    print()
    print("   # Pipeline simples (mais rápido)")
    print("   resultados = executar_pipeline_simples(df_com_target)")
    print()
    print("   # Salvar modelo final")
    print("   salvar_modelo_final(melhor_modelo, feature_names)")
    print()
    print("✅ Módulo pronto para uso!")