"""
Módulo principal de balanceamento de dados
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score

from data_preparation import preparar_dados_para_balanceamento
from config import BALANCING_STRATEGIES, DEFAULT_CONFIG


def executar_balanceamento_completo(df_com_target):
    """
    Executa balanceamento completo com análise e comparação
    
    Args:
        df_com_target: DataFrame com target de viabilidade
        
    Returns:
        dict: Resultados da análise completa
    """
    print("🚀 EXECUÇÃO COMPLETA DO BALANCEAMENTO")
    print("=" * 50)
    
    # 1. Preparar dados
    X, y, feature_names = preparar_dados_para_balanceamento(df_com_target)
    
    # 2. Inicializar balanceador (assumindo que DataBalancer existe das partes anteriores)
    try:
        balancer = DataBalancer(random_state=DEFAULT_CONFIG['random_state'])
    except NameError:
        print("❌ DataBalancer não encontrado. Execute as partes 1 e 2 primeiro.")
        return None
    
    # 3. Analisar desbalanceamento atual
    imbalance_info = balancer.analyze_imbalance(
        X.values, y.values,
        target_names={0: 'NÃO VIÁVEL', 1: 'VIÁVEL'}
    )
    
    # 4. Criar datasets com diferentes estratégias
    print("\n🔄 Testando diferentes estratégias...")
    
    balanced_datasets = balancer.create_balanced_datasets(
        X.values, y.values,
        strategies=BALANCING_STRATEGIES
    )
    
    # 5. Avaliar estratégias
    if balanced_datasets:
        print("\n📈 Avaliando estratégias...")
        results = balancer.evaluate_strategies(test_size=DEFAULT_CONFIG['test_size'])
        
        # 6. Encontrar melhor estratégia
        best_strategy_name, best_strategy_data = balancer.get_best_strategy(metric='macro_f1')
        
        return {
            'balancer': balancer,
            'X_original': X,
            'y_original': y,
            'feature_names': feature_names,
            'imbalance_info': imbalance_info,
            'balanced_datasets': balanced_datasets,
            'evaluation_results': results,
            'best_strategy': best_strategy_name,
            'best_data': best_strategy_data
        }
    else:
        print("❌ Nenhuma estratégia foi executada com sucesso")
        return None


def criar_dataset_final_balanceado(df_com_target, strategy='moderate', save_file=True):
    """
    Cria o dataset final balanceado para treino de modelos
    
    Args:
        df_com_target: DataFrame com target
        strategy: Estratégia de balanceamento
        save_file: Se deve salvar arquivo
        
    Returns:
        tuple: (df_balanced, X_balanced, y_balanced, feature_names)
    """
    print("🎯 CRIANDO DATASET FINAL BALANCEADO")
    print("=" * 40)
    
    # Preparar dados
    X, y, feature_names = preparar_dados_para_balanceamento(df_com_target)
    
    # Inicializar balanceador
    try:
        balancer = DataBalancer(random_state=DEFAULT_CONFIG['random_state'])
    except NameError:
        print("❌ DataBalancer não encontrado. Execute as partes 1 e 2 primeiro.")
        return None, None, None, None
    
    # Criar dataset balanceado final
    X_balanced, y_balanced = balancer.create_final_balanced_dataset(
        X.values, y.values,
        strategy=strategy
    )
    
    # Criar DataFrame final
    df_balanced = pd.DataFrame(X_balanced, columns=feature_names)
    df_balanced['Viavel'] = y_balanced
    
    print(f"\n✅ Dataset balanceado criado!")
    print(f"📊 Shape: {df_balanced.shape}")
    print(f"🎯 Distribuição final:")
    target_dist = df_balanced['Viavel'].value_counts()
    for val, count in target_dist.items():
        label = 'VIÁVEL' if val == 1 else 'NÃO VIÁVEL'
        print(f"   {label}: {count:,} ({count/len(df_balanced)*100:.1f}%)")
    
    # Salvar arquivo se solicitado
    if save_file:
        filename = 'SINDEC_balanced_dataset.csv'
        df_balanced.to_csv(filename, index=False)
        print(f"\n💾 Arquivo salvo: {filename}")
    
    return df_balanced, X_balanced, y_balanced, feature_names


def comparar_performance_pre_pos_balanceamento(df_com_target):
    """
    Compara performance de modelo simples antes/depois do balanceamento
    
    Args:
        df_com_target: DataFrame com target
        
    Returns:
        dict: Resultados da comparação
    """
    print("📊 COMPARAÇÃO PRÉ/PÓS BALANCEAMENTO")
    print("=" * 40)
    
    # Preparar dados originais
    X, y, feature_names = preparar_dados_para_balanceamento(df_com_target)
    
    # Split original
    X_train_orig, X_test_orig, y_train_orig, y_test_orig = train_test_split(
        X, y, test_size=DEFAULT_CONFIG['test_size'], 
        random_state=DEFAULT_CONFIG['random_state'], stratify=y
    )
    
    # Modelo nos dados originais
    print("1️⃣ DADOS ORIGINAIS (DESBALANCEADOS):")
    model_orig = RandomForestClassifier(
        n_estimators=DEFAULT_CONFIG['n_estimators'], 
        random_state=DEFAULT_CONFIG['random_state']
    )
    model_orig.fit(X_train_orig, y_train_orig)
    
    y_pred_orig = model_orig.predict(X_test_orig)
    y_proba_orig = model_orig.predict_proba(X_test_orig)[:, 1]
    
    auc_orig = roc_auc_score(y_test_orig, y_proba_orig)
    print(f"   AUC: {auc_orig:.3f}")
    print("   Classification Report:")
    print(classification_report(y_test_orig, y_pred_orig,
                              target_names=['NÃO VIÁVEL', 'VIÁVEL']))
    
    # Dados balanceados
    print("\n2️⃣ DADOS BALANCEADOS:")
    try:
        balancer = DataBalancer(random_state=DEFAULT_CONFIG['random_state'])
        X_balanced, y_balanced = balancer.create_final_balanced_dataset(
            X.values, y.values, strategy='moderate'
        )
        
        # Split balanceado
        X_train_bal, X_test_bal, y_train_bal, y_test_bal = train_test_split(
            X_balanced, y_balanced, test_size=DEFAULT_CONFIG['test_size'], 
            random_state=DEFAULT_CONFIG['random_state'], stratify=y_balanced
        )
        
        # Modelo nos dados balanceados
        model_bal = RandomForestClassifier(
            n_estimators=DEFAULT_CONFIG['n_estimators'], 
            random_state=DEFAULT_CONFIG['random_state']
        )
        model_bal.fit(X_train_bal, y_train_bal)
        
        y_pred_bal = model_bal.predict(X_test_bal)
        y_proba_bal = model_bal.predict_proba(X_test_bal)[:, 1]
        
        auc_bal = roc_auc_score(y_test_bal, y_proba_bal)
        print(f"   AUC: {auc_bal:.3f}")
        print("   Classification Report:")
        print(classification_report(y_test_bal, y_pred_bal,
                                  target_names=['NÃO VIÁVEL', 'VIÁVEL']))
        
        print(f"\n📈 MELHORIA:")
        print(f"   AUC: {auc_orig:.3f} → {auc_bal:.3f} ({auc_bal-auc_orig:+.3f})")
        
        return {
            'auc_original': auc_orig,
            'auc_balanced': auc_bal,
            'improvement': auc_bal - auc_orig,
            'model_original': model_orig,
            'model_balanced': model_bal
        }
        
    except NameError:
        print("❌ DataBalancer não encontrado. Execute as partes 1 e 2 primeiro.")
        return {
            'auc_original': auc_orig,
            'auc_balanced': None,
            'improvement': None,
            'model_original': model_orig,
            'model_balanced': None
        }


def aplicar_balanceamento_sindec(df_com_target, strategy='moderate', run_analysis=True):
    """
    Função principal para aplicar balanceamento aos dados SINDEC
    
    Args:
        df_com_target: DataFrame com target de viabilidade criado
        strategy: 'conservative', 'moderate', 'aggressive', ou 'auto'
        run_analysis: Se deve executar análise completa (demora mais)
        
    Returns:
        tuple: (df_balanced, results)
    """
    print("🎯 APLICANDO BALANCEAMENTO AOS DADOS SINDEC")
    print("=" * 55)
    
    results = {}
    
    if run_analysis:
        # Execução completa com análise
        print("📊 Executando análise completa...")
        analysis_results = executar_balanceamento_completo(df_com_target)
        results['analysis'] = analysis_results
        
        # Comparação de performance
        print("\n📈 Comparando performance...")
        performance_results = comparar_performance_pre_pos_balanceamento(df_com_target)
        results['performance'] = performance_results
    
    # Criar dataset final
    print(f"\n🎯 Criando dataset final com estratégia '{strategy}'...")
    df_balanced, X_balanced, y_balanced, feature_names = criar_dataset_final_balanceado(
        df_com_target, strategy=strategy
    )
    
    if df_balanced is not None:
        results['final_dataset'] = {
            'df_balanced': df_balanced,
            'X_balanced': X_balanced,
            'y_balanced': y_balanced,
            'feature_names': feature_names
        }
        
        print("\n✅ BALANCEAMENTO CONCLUÍDO!")
        print(f"🎯 Próximo passo: Treinar modelos de ML com df_balanced")
        
        return df_balanced, results
    else:
        print("❌ Erro ao criar dataset balanceado")
        return None, results