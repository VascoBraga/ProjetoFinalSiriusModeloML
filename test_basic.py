"""
Testes básicos para verificar se os módulos estão funcionando
"""

import pandas as pd
import numpy as np
import sys
import os


def criar_dados_mock():
    """Cria dados simulados para teste"""
    print("📊 Criando dados simulados para teste...")
    
    np.random.seed(42)
    n_samples = 1000
    
    # Cria dados simulados
    data = {
        'ValorCausa': np.random.lognormal(8, 1, n_samples),
        'ValorCausaConfianca': np.random.uniform(0.5, 1.0, n_samples),
        'AnoCalendario': np.random.choice([2020, 2021, 2022], n_samples),
        'UF': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR'], n_samples),
        'Regiao': np.random.choice(['Sudeste', 'Sul', 'Nordeste'], n_samples),
        'SexoConsumidor': np.random.choice(['M', 'F'], n_samples),
        'FaixaEtariaConsumidor': np.random.choice([
            'entre 21 a 30 anos', 'entre 31 a 40 anos', 'entre 41 a 50 anos'
        ], n_samples),
        'CodigoAssunto': np.random.choice([1, 2, 3, 4, 5], n_samples),
        'CodigoProblema': np.random.choice([10, 20, 30, 40], n_samples),
        
        # Features que serão removidas (data leakage)
        'Score_Valor': np.random.uniform(0, 1, n_samples),
        'Score_Sucesso': np.random.uniform(0, 1, n_samples),
        'Score_Total': np.random.uniform(0, 1, n_samples),
        'Taxa_Sucesso': np.random.uniform(0, 1, n_samples),
        'Potencial_Financeiro': np.random.uniform(0, 1, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Cria target baseado em algumas regras simples
    target_score = (
        (df['ValorCausa'] > df['ValorCausa'].median()).astype(int) * 0.3 +
        (df['ValorCausaConfianca'] > 0.8).astype(int) * 0.3 +
        (df['UF'].isin(['SP', 'RJ'])).astype(int) * 0.2 +
        np.random.uniform(0, 0.2, n_samples)
    )
    
    # Target desbalanceado (mais casos viáveis)
    df['Viavel'] = (target_score > 0.4).astype(int)
    
    print(f"✅ Dados criados: {df.shape}")
    print(f"📊 Distribuição target: {df['Viavel'].value_counts().to_dict()}")
    
    return df


def testar_imports():
    """Testa se todos os módulos podem ser importados"""
    print("\n🔍 TESTANDO IMPORTS")
    print("=" * 30)
    
    try:
        import config
        print("✅ config.py importado")
    except Exception as e:
        print(f"❌ Erro ao importar config: {e}")
        return False
    
    try:
        import data_preparation
        print("✅ data_preparation.py importado")
    except Exception as e:
        print(f"❌ Erro ao importar data_preparation: {e}")
        return False
    
    try:
        import clean_features
        print("✅ clean_features.py importado")
    except Exception as e:
        print(f"❌ Erro ao importar clean_features: {e}")
        return False
    
    try:
        import model_training
        print("✅ model_training.py importado")
    except Exception as e:
        print(f"❌ Erro ao importar model_training: {e}")
        return False
    
    try:
        import balancing
        print("✅ balancing.py importado")
    except Exception as e:
        print(f"❌ Erro ao importar balancing: {e}")
        return False
    
    try:
        import main
        print("✅ main.py importado")
    except Exception as e:
        print(f"❌ Erro ao importar main: {e}")
        return False
    
    return True


def testar_preparacao_dados():
    """Testa preparação de dados"""
    print("\n🔧 TESTANDO PREPARAÇÃO DE DADOS")
    print("=" * 35)
    
    try:
        from data_preparation import preparar_dados_para_balanceamento
        
        df_mock = criar_dados_mock()
        X, y, features = preparar_dados_para_balanceamento(df_mock)
        
        print(f"✅ Preparação concluída")
        print(f"📊 Shape X: {X.shape}")
        print(f"📊 Shape y: {y.shape}")
        print(f"📋 Features: {len(features)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na preparação: {e}")
        return False


def testar_features_limpas():
    """Testa criação de features limpas"""
    print("\n🧹 TESTANDO FEATURES LIMPAS")
    print("=" * 30)
    
    try:
        from clean_features import preparar_dados_limpos
        
        df_mock = criar_dados_mock()
        X, y, features = preparar_dados_limpos(df_mock)
        
        if X is not None:
            print(f"✅ Features limpas criadas")
            print(f"📊 Shape X: {X.shape}")
            print(f"📊 Shape y: {y.shape}")
            print(f"📋 Features finais: {len(features)}")
            return True
        else:
            print("❌ X é None")
            return False
            
    except Exception as e:
        print(f"❌ Erro nas features: {e}")
        return False


def testar_treinamento():
    """Testa treinamento de modelos"""
    print("\n🤖 TESTANDO TREINAMENTO")
    print("=" * 25)
    
    try:
        from model_training import treinar_modelo_limpo
        
        df_mock = criar_dados_mock()
        resultados, X_train, X_test, y_train, y_test, features = treinar_modelo_limpo(df_mock)
        
        if resultados is not None:
            print(f"✅ Treinamento concluído")
            print(f"📊 Modelos testados: {len(resultados)}")
            
            for nome, resultado in resultados.items():
                print(f"   {nome}: AUC = {resultado['auc']:.3f}")
            
            return True
        else:
            print("❌ Resultados é None")
            return False
            
    except Exception as e:
        print(f"❌ Erro no treinamento: {e}")
        return False


def testar_pipeline_simples():
    """Testa pipeline simplificado"""
    print("\n⚡ TESTANDO PIPELINE SIMPLES")
    print("=" * 30)
    
    try:
        # Como DataBalancer pode não estar disponível, vamos simular
        print("⚠️  Nota: DataBalancer das partes 1 e 2 pode não estar disponível")
        print("    Este teste verifica apenas a estrutura dos módulos")
        
        from main import executar_pipeline_simples
        
        # Não executa de fato pois pode faltar DataBalancer
        print("✅ Função importada com sucesso")
        print("📝 Para teste completo, execute com DataBalancer disponível")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no pipeline: {e}")
        return False


def executar_todos_testes():
    """Executa todos os testes"""
    print("🧪 EXECUTANDO TESTES BÁSICOS")
    print("=" * 40)
    
    testes = [
        ("Imports", testar_imports),
        ("Preparação de Dados", testar_preparacao_dados),
        ("Features Limpas", testar_features_limpas),
        ("Treinamento", testar_treinamento),
        ("Pipeline Simples", testar_pipeline_simples)
    ]
    
    resultados = []
    
    for nome, funcao_teste in testes:
        print(f"\n{'='*50}")
        print(f"TESTE: {nome}")
        print(f"{'='*50}")
        
        try:
            sucesso = funcao_teste()
            resultados.append((nome, sucesso))
        except Exception as e:
            print(f"❌ Erro inesperado em {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    print(f"\n{'='*50}")
    print("📊 RESUMO DOS TESTES")
    print(f"{'='*50}")
    
    sucessos = 0
    for nome, sucesso in resultados:
        status = "✅ PASSOU" if sucesso else "❌ FALHOU"
        print(f"{nome:20} : {status}")
        if sucesso:
            sucessos += 1
    
    print(f"\n🎯 RESULTADO FINAL: {sucessos}/{len(testes)} testes passaram")
    
    if sucessos == len(testes):
        print("✅ Todos os testes passaram! Módulos prontos para uso.")
    else:
        print("⚠️  Alguns testes falharam. Verifique as dependências.")
        print("💡 Lembre-se: DataBalancer das partes 1 e 2 é necessário para uso completo.")
    
    return sucessos == len(testes)


if __name__ == "__main__":
    print("🎯 TESTES BÁSICOS - ALGORITMO SINDEC PARTE 3")
    print("=" * 60)
    
    # Verifica se está no diretório correto
    arquivos_necessarios = [
        'config.py', 'data_preparation.py', 'balancing.py',
        'clean_features.py', 'model_training.py', 'main.py'
    ]
    
    faltando = []
    for arquivo in arquivos_necessarios:
        if not os.path.exists(arquivo):
            faltando.append(arquivo)
    
    if faltando:
        print(f"❌ Arquivos não encontrados: {faltando}")
        print("💡 Execute este teste no diretório com todos os módulos")
        sys.exit(1)
    
    # Executa testes
    sucesso = executar_todos_testes()
    
    if sucesso:
        print("\n🚀 Pronto para usar o algoritmo!")
        print("📝 Próximos passos:")
        print("   1. Certifique-se de ter a classe DataBalancer das partes 1 e 2")
        print("   2. Execute: python example.py")
        print("   3. Use: from main import executar_pipeline_completo")
    else:
        print("\n🔧 Ajustes necessários antes do uso completo")
    
    sys.exit(0 if sucesso else 1)