"""
Exemplo de uso dos módulos do sistema de classificação de viabilidade jurídica.

Este arquivo demonstra como usar cada módulo separadamente para maior controle
sobre o processo de preparação dos dados.
"""

import pandas as pd
import numpy as np

# Imports dos módulos do sistema
from data_preprocessing import preprocessar_dados
from exploratory_analysis import ViabilidadeCausasAnalyzer, executar_etapa_1
from target_creation import TargetCreator, executar_etapa_2
from feature_engineering import ViabilidadeFeatureEngineer, executar_feature_engineering
from data_balancing import DataBalancer, balancear_dados_viabilidade
from utils import debug_dataframe, verificar_colunas_necessarias, imprimir_estatisticas_resumidas
from main import ViabilidadeClassificationPipeline


def exemplo_pipeline_completo():
    """
    Exemplo 1: Uso do pipeline completo (mais simples)
    """
    print("=" * 80)
    print("EXEMPLO 1: PIPELINE COMPLETO")
    print("=" * 80)
    
    # Inicializa pipeline
    pipeline = ViabilidadeClassificationPipeline()
    
    # Executa tudo de uma vez
    resultados = pipeline.executar_pipeline_completo(
        filepath="dados_sindec.csv",
        incluir_tfidf=False,  # False para ser mais rápido
        estrategia_balanceamento='moderate'
    )
    
    if resultados:
        print("✅ Pipeline executado com sucesso!")
        print(f"Dados prontos para ML: {resultados['X_balanced'].shape}")
    
    return resultados


def exemplo_execucao_passo_a_passo():
    """
    Exemplo 2: Execução passo a passo (mais controle)
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 2: EXECUÇÃO PASSO A PASSO")
    print("=" * 80)
    
    # 1. CARREGAMENTO DOS DADOS
    print("\n1️⃣ CARREGANDO DADOS...")
    df_original = pd.read_csv("dados_sindec.csv")
    print(f"Dados carregados: {df_original.shape}")
    
    # Debug inicial
    debug_dataframe(df_original, "Original")
    
    # 2. PREPROCESSAMENTO
    print("\n2️⃣ PREPROCESSAMENTO...")
    df_processado = preprocessar_dados(df_original)
    imprimir_estatisticas_resumidas(df_processado, "Preprocessado")
    
    # 3. ANÁLISE EXPLORATÓRIA DETALHADA
    print("\n3️⃣ ANÁLISE EXPLORATÓRIA...")
    analyzer = ViabilidadeCausasAnalyzer(df_processado)
    
    # Executar análises específicas
    analyzer.definir_problema()
    stats_basicas = analyzer.análise_exploratória_básica()
    analise_assuntos = analyzer.analisar_padrões_por_assunto(top_n=10)
    distribuicoes = analyzer.analisar_distribuições()
    insights = analyzer.identificar_insights_preliminares()
    
    print(f"✅ Análise concluída. Taxa de sucesso média: {stats_basicas['taxa_sucesso']:.1%}")
    
    # 4. CRIAÇÃO DO TARGET COM CONTROLE PERSONALIZADO
    print("\n4️⃣ CRIAÇÃO DO TARGET...")
    target_creator = TargetCreator(df_processado)
    
    # Passo a passo da criação do target
    stats_assuntos, stats_problemas = target_creator.calcular_estatisticas_historicas()
    criterios = target_creator.definir_criterios_viabilidade()
    df_com_target = target_creator.criar_variavel_target()
    analise_target = target_creator.analisar_target_criado()
    target_creator.validar_criterios()
    
    print(f"✅ Target criado. Distribuição: {analise_target['distribuicao_target']}")
    
    # 5. FEATURE ENGINEERING CUSTOMIZADO
    print("\n5️⃣ FEATURE ENGINEERING...")
    fe = ViabilidadeFeatureEngineer()
    
    # Aplicar transformações específicas
    df_texto = fe.extrair_features_texto(df_com_target)
    print(f"Após features de texto: {df_texto.shape}")
    
    df_categoricas = fe.criar_features_categoricas(df_texto)
    print(f"Após features categóricas: {df_categoricas.shape}")
    
    df_numericas = fe.criar_features_numericas(df_categoricas)
    print(f"Após features numéricas: {df_numericas.shape}")
    
    # TF-IDF opcional (comentado por ser lento)
    # df_tfidf = fe.processar_texto_avancado(df_numericas, max_features=50)
    # print(f"Após TF-IDF: {df_tfidf.shape}")
    
    df_features = df_numericas  # ou df_tfidf se usar TF-IDF
    
    # Preparar para ML
    X, y, feature_names = fe.preparar_para_ml(df_features, target_col='Viavel')
    print(f"✅ Dados preparados para ML: X{X.shape}, y{y.shape}")
    
    # 6. BALANCEAMENTO AVANÇADO
    print("\n6️⃣ BALANCEAMENTO AVANÇADO...")
    balancer = DataBalancer(random_state=42)
    
    # Analisar desbalanceamento
    analise_desbalanceamento = balancer.analyze_imbalance(
        X, y, {0: 'NÃO VIÁVEL', 1: 'VIÁVEL'}
    )
    
    # Testar múltiplas estratégias
    estrategias_para_testar = ['smote', 'borderline_smote', 'hybrid_custom']
    datasets_balanceados = balancer.create_balanced_datasets(
        X, y, strategies=estrategias_para_testar
    )
    
    # Avaliar estratégias
    if len(datasets_balanceados) > 0:
        resultados_avaliacao = balancer.evaluate_strategies(test_size=0.3)
        melhor_estrategia, melhor_dados = balancer.get_best_strategy(metric='macro_f1')
        
        X_balanced = melhor_dados['X']
        y_balanced = melhor_dados['y']
    else:
        print("⚠️ Usando balanceamento simples...")
        X_balanced, y_balanced = balancer.create_final_balanced_dataset(
            X, y, strategy='moderate'
        )
    
    print(f"✅ Dados balanceados: {X_balanced.shape}")
    
    # 7. SALVAR RESULTADOS
    print("\n7️⃣ SALVANDO RESULTADOS...")
    
    # Salvar DataFrames intermediários
    df_processado.to_csv('exemplo_dados_preprocessados.csv', index=False)
    df_com_target.to_csv('exemplo_dados_com_target.csv', index=False)
    df_features.to_csv('exemplo_dados_com_features.csv', index=False)
    
    # Salvar dados finais para ML
    df_final = pd.DataFrame(X_balanced, columns=feature_names)
    df_final['target'] = y_balanced
    df_final.to_csv('exemplo_dados_finais_ml.csv', index=False)
    
    print("✅ Todos os arquivos salvos com prefixo 'exemplo_'")
    
    return {
        'df_original': df_original,
        'df_processado': df_processado,
        'df_com_target': df_com_target,
        'df_features': df_features,
        'X_balanced': X_balanced,
        'y_balanced': y_balanced,
        'feature_names': feature_names,
        'analise_target': analise_target,
        'stats_basicas': stats_basicas
    }


def exemplo_uso_especifico_modulos():
    """
    Exemplo 3: Uso específico de módulos individuais
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 3: USO ESPECÍFICO DE MÓDULOS")
    print("=" * 80)
    
    # Supondo que já temos dados preprocessados
    try:
        df = pd.read_csv("dados_preprocessados.csv")
        print(f"✅ Dados carregados: {df.shape}")
    except FileNotFoundError:
        print("❌ Arquivo 'dados_preprocessados.csv' não encontrado.")
        print("Execute o exemplo 1 ou 2 primeiro para gerar os dados.")
        return None
    
    # Exemplo: Apenas análise exploratória
    print("\n🔍 ANÁLISE EXPLORATÓRIA FOCADA...")
    analyzer = ViabilidadeCausasAnalyzer(df)
    
    # Análise específica de assuntos com alto potencial
    analise_assuntos = analyzer.analisar_padrões_por_assunto(top_n=5)
    print("Top 5 assuntos mais promissores identificados.")
    
    # Exemplo: Apenas feature engineering de texto
    print("\n📝 FEATURE ENGINEERING DE TEXTO...")
    fe = ViabilidadeFeatureEngineer()
    df_com_features_texto = fe.extrair_features_texto(df)
    
    # Verificar features criadas
    features_texto = [col for col in df_com_features_texto.columns 
                     if col not in df.columns]
    print(f"Features de texto criadas: {len(features_texto)}")
    for feature in features_texto[:10]:  # Mostra primeiras 10
        print(f"  - {feature}")
    
    # Exemplo: Apenas balanceamento simples
    if 'Viavel' in df.columns:
        print("\n⚖️ BALANCEAMENTO SIMPLES...")
        X_bal, y_bal, features, balancer = balancear_dados_viabilidade(
            df, strategy='conservative'
        )
        print(f"Dados balanceados: {X_bal.shape}")
    
    print("✅ Exemplos de uso específico concluídos.")


def exemplo_validacoes():
    """
    Exemplo 4: Como usar as funções de validação
    """
    print("\n" + "=" * 80)
    print("EXEMPLO 4: VALIDAÇÕES E QUALIDADE DOS DADOS")
    print("=" * 80)
    
    try:
        df = pd.read_csv("dados_preprocessados.csv")
    except FileNotFoundError:
        print("❌ Execute os exemplos anteriores primeiro.")
        return
    
    # Validações por etapa
    from utils import validar_pipeline_input, criar_relatorio_qualidade_dados
    
    print("\n✅ VALIDANDO ENTRADA PARA CADA ETAPA...")
    
    etapas = ['preprocessamento', 'analise_exploratoria', 'criacao_target', 
              'feature_engineering', 'balanceamento']
    
    for etapa in etapas:
        valido = validar_pipeline_input(df, etapa)
        status = "✅" if valido else "❌"
        print(f"{status} {etapa}")
    
    # Relatório de qualidade
    print("\n📊 GERANDO RELATÓRIO DE QUALIDADE...")
    relatorio = criar_relatorio_qualidade_dados(df, "relatorio_exemplo.txt")
    print("Relatório salvo em 'relatorio_exemplo.txt'")


if __name__ == "__main__":
    print("🎯 EXEMPLOS DE USO DO SISTEMA DE VIABILIDADE JURÍDICA")
    print("=" * 80)
    
    print("\nEscolha o exemplo para executar:")
    print("1. Pipeline completo (mais simples)")
    print("2. Execução passo a passo (mais controle)")
    print("3. Uso específico de módulos")
    print("4. Validações e qualidade")
    print("5. Executar todos os exemplos")
    
    escolha = input("\nDigite o número do exemplo (1-5): ").strip()
    
    if escolha == "1":
        exemplo_pipeline_completo()
    elif escolha == "2":
        exemplo_execucao_passo_a_passo()
    elif escolha == "3":
        exemplo_uso_especifico_modulos()
    elif escolha == "4":
        exemplo_validacoes()
    elif escolha == "5":
        print("\n🚀 EXECUTANDO TODOS OS EXEMPLOS...")
        exemplo_pipeline_completo()
        exemplo_execucao_passo_a_passo()
        exemplo_uso_especifico_modulos()
        exemplo_validacoes()
        print("\n✅ TODOS OS EXEMPLOS EXECUTADOS!")
    else:
        print("❌ Opção inválida. Execute o script novamente.")
    
    print("\n🎯 Exemplos concluídos! Verifique os arquivos gerados.")